#!/usr/bin/env python3
import itertools  
# from pprint import pprint
import logging
import time
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from src.mechanism_encoder.rand_response_count_encoder import RandResponseCountEncoder
import src.inference.inference as inference
import src.accuracy as accuracy
import math
import signal

def timeout_handler(signum, frame):
    print("Inference Timed Out")
    raise TimeoutError("Inference timed out")

class RunAccuracy(object):
    def __init__(self,mechanism, alpha, mechanism_params,inference_method,accuracy_set,timeout,official,get_examples):
        self.mechanism, self.alpha, self.mechanism_params, self.inference_method, self.accuracy_set, self.timeout, self.official, self.get_examples = mechanism, alpha, mechanism_params,inference_method,accuracy_set,timeout,official,get_examples

    def run(self):
        total_start_time = time.time()

        ##################
        # INITIALIZATION #
        ##################
        logging.info(f'\n\n-----------------------------------------------------------\n INITIALIZING PROGRAM \n-----------------------------------------------------------\n')

        ### Configuration
        mechanism = self.mechanism
        mechanism_params = self.mechanism_params
        inference_method = self.inference_method
        accuracy_set = self.accuracy_set


        ### Mechanism Params 
        params_string = '_'.join([f"{k}-{mechanism_params[k]}" for k in mechanism_params])
        if not self.official:
            mechanism_pth = Path(f"temp_results/mechanisms/{mechanism}/{inference_method}/{params_string}")
        else:
            mechanism_pth = Path(f"final_results/mechanisms/{mechanism}/{inference_method}/{params_string}")
        mechanism_pth.mkdir(parents=True, exist_ok=True)

        
        # For dice we do all outputs because that is what it computes anyways
        if accuracy_set == 'exhaustive' and mechanism == 'rr_count':
            S_inputs = list(itertools.product([False,True], repeat=mechanism_params['n']))
            S_outputs = list(range(mechanism_params['n']+1))
        elif accuracy_set == 'min_representative' and mechanism == 'rr_count':
            S_inputs = [tuple([True if j >= i else False for j in range(mechanism_params['n'])]) for i in range(mechanism_params['n']+1)]
            S_outputs = list(range(mechanism_params['n']+1))
        else: raise NotImplementedError(f'S_inf = {accuracy_set} not implemented for {mechanism}')


        ### File Params
        if not self.official:
            stats_pth = Path(f"test_results/stats/{inference_method}/acc-{accuracy_set}_alpha-{self.alpha}/{mechanism}/{params_string}")
        else:
            if self.get_examples:
                stats_pth = Path(f"final_results/examples/{inference_method}/acc-{accuracy_set}_alpha-{self.alpha}/{mechanism}/{params_string}")
            else:
                stats_pth = Path(f"final_results/stats/{inference_method}/acc-{accuracy_set}_alpha-{self.alpha}/{mechanism}/{params_string}")
        stats_pth.mkdir(parents=True, exist_ok=True)

        ### Scalability DF
        scalability_file = stats_pth / 'scalability.csv'
        scalability_df = pd.Series()

        ### Stats DF
        stats_file = stats_pth / 'stats.csv'
        stats_df = pd.Series()
        inference_probmat_file = stats_pth / 'inference_probmat.csv'
        unique_probs_file = stats_pth / 'unique_probs.csv'

        if mechanism == 'rr_count':
            self.__store_values(stats_df, 'N', mechanism_params['n'], stats_file)
            self.__store_values(stats_df, 'lambda', mechanism_params['lamb'], stats_file)
        else: raise NotImplementedError(f'No stats initialization for {mechanism} mechanism')

        self.__store_values(stats_df, 'num_unique_probabilities', -1, stats_file)
        self.__store_values(stats_df, 'best_error',-1, stats_file)
        self.__store_values(stats_df, 'best_input', None, stats_file)


        ### Logging Params
        # Initialize logger, from: https://stackoverflow.com/a/13733863
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        rootLogger = logging.getLogger()
        logs_pth = Path(f"logs")
        logs_pth.mkdir(parents=True, exist_ok=True)
        file_base = f'{inference_method}_{mechanism}_{params_string}_acc-{accuracy_set}'
        fileHandler = logging.FileHandler(logs_pth / f'{file_base}.log')
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)
        rootLogger.setLevel(logging.INFO)



        #########################
        # FILES GENERATION #
        #########################

        logging.info(f'\n\n-----------------------------------------------------------\n GENERATING FILES ({inference_method, mechanism, mechanism_params}) \n-----------------------------------------------------------\n')

        file_write_start = time.time()
        # Initialize encoder
        if mechanism == 'rr_count':
            mechanism_encoder = RandResponseCountEncoder(mechanism_params=mechanism_params, outfiles_dir=mechanism_pth)
        else: raise NotImplementedError

        if inference_method == 'dice_flat':
            mechanism_encoder.dice_flat_encoder(S_inputs=S_inputs)
        else: raise NotImplementedError

        self.__store_values(scalability_df,'file_write_time', time.time()-file_write_start, scalability_file)


        ##################
        # INFERENCE #
        ##################
        logging.info(f'\n\n-----------------------------------------------------------\n INFERENCE ({inference_method} {mechanism} {mechanism_params}) \n-----------------------------------------------------------\n')
        # Set up timeout for inference
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.timeout) 
        timed_out = False
        try:
            # Run inference 
            if inference_method == 'dice_flat':
                inference_timeseries, inference_probmat = inference.run_dice(S_inputs=S_inputs,S_outputs=S_outputs,mechanism_filepath=mechanism_pth,stats_pth=stats_pth)
            else: raise NotImplementedError

            # Gather stats
            probmat_df = pd.DataFrame(inference_probmat)
            unique_probs = np.unique(probmat_df)

            self.__store_values(stats_df, 'num_unique_probabilities', len(unique_probs), stats_file)
            self.__store_values(scalability_df, 'total_inference_time',inference_timeseries.sum(), scalability_file)
            self.__store_values(scalability_df, 'mean_inf_time_per_call',inference_timeseries.mean(), scalability_file)
            self.__store_values(scalability_df, 'num_inference_calls',inference_timeseries.count(), scalability_file)

            # Save stats files
            probmat_df.to_csv(inference_probmat_file)
            pd.Series(unique_probs).to_csv(unique_probs_file)
            stats_df.to_csv(stats_file)

        except TimeoutError:
            self.__store_values(scalability_df, 'total_inference_time',f"TIMEOUT ({self.timeout} seconds)", scalability_file)
            self.__store_values(scalability_df, 'mean_inf_time_per_call',f"TIMEOUT ({self.timeout} seconds)", scalability_file)
            self.__store_values(scalability_df, 'num_inference_calls',f"TIMEOUT ({self.timeout} seconds)", scalability_file)
            stats_df.to_csv(stats_file)
            timed_out = True

        ################
        # ACCURACY     #
        ################
        logging.info(f'\n\n-----------------------------------------------------------\n ACCURACY ({inference_method} {mechanism} {mechanism_params}) \n-----------------------------------------------------------\n')


        # Formula for accuracy: Pr[|F(x) - F_DP(x)| < alpha] >= beta
        # Minimize sum_y=(V_x - alpha, V_x + alpha) M[x,y]
        # For each x in inference set
        if not timed_out:
            # Optional to get all the assignments and their corresponding accuracies
            if self.get_examples:
                accuracy.get_examples(S_inputs=S_inputs,inference_probmat=inference_probmat,alpha=self.alpha,mechanism_encoder=mechanism_encoder,examples_file=stats_pth/'examples.csv')
                print('got examples!')
                exit(0)
            
            # Otherwise, just get accuracy bounds
            start_accuracy = time.time()
            accuracy_err, accuracy_bounding_assn = accuracy.run_accuracy(S_inputs=S_inputs,inference_probmat=inference_probmat,alpha=self.alpha,mechanism_encoder=mechanism_encoder)

            # Save stats
            self.__store_values(scalability_df, 'accuracy_time', time.time() - start_accuracy, scalability_file)
            print('accuracy', accuracy_err, accuracy_bounding_assn)
            self.__store_values(stats_df, 'accuracy_err', accuracy_err, stats_file)
            self.__store_values(stats_df, 'accuracy_bounding_assn', accuracy_bounding_assn, stats_file)
            logging.info(f'\nBest param is ({self.alpha},{1-accuracy_err})-Accuracy for {mechanism} {mechanism_params}\n For accuracy bounding assignment: x = {accuracy_bounding_assn}.\n')
            total_duration = time.time() - total_start_time
            total_experiment_time = scalability_df['file_write_time'] + scalability_df['total_inference_time'] + scalability_df['accuracy_time']
            self.__store_values(scalability_df, 'total_experiment_time', total_experiment_time, scalability_file)
            self.__store_values(scalability_df, 'total_duration', total_duration, scalability_file)
            self.__store_values(scalability_df, 'python_misc_time', total_duration - total_experiment_time, scalability_file)
    
    def __store_values(self, df, key, value, pth):
        df.at[key] = value
        df.to_csv(pth)
