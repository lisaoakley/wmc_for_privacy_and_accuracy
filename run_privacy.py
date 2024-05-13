#!/usr/bin/env python3
import itertools  
# from pprint import pprint
import logging
import time
import sys
import pandas as pd
import numpy as np
import signal
from pathlib import Path
from src.mechanism_encoder.rand_response_encoder import RandResponseEncoder
from src.mechanism_encoder.geometric_above_encoder import GeometricAboveEncoder
import src.inference.inference as inference
import src.comparison as comparison
import math

def timeout_handler(signum, frame):
    print("Inference Timed Out")
    raise TimeoutError("Inference timed out")

class RunPrivacy(object):
    def __init__(self,mechanism, mechanism_params,inference_method,inference_set,comparison_set,timeout,official,get_examples):
        self.mechanism, self.mechanism_params, self.inference_method, self.inference_set, self.comparison_set, self.timeout, self.official, self.get_examples = mechanism, mechanism_params,inference_method,inference_set,comparison_set, timeout, official, get_examples

    def run(self):
        timed_out = False
        total_start_time = time.time()

        ##################
        # INITIALIZATION #
        ##################
        logging.info(f'\n\n-----------------------------------------------------------\n INITIALIZING PROGRAM \n-----------------------------------------------------------\n')

        ### Configuration
        mechanism = self.mechanism
        mechanism_params = self.mechanism_params
        inference_method = self.inference_method
        inference_set = self.inference_set
        comparison_set = self.comparison_set


        ### Mechanism Params 
        params_string = '_'.join([f"{k}-{mechanism_params[k]}" for k in mechanism_params])
        if not self.official:
            mechanism_pth = Path(f"test_results/mechanisms/{mechanism}/{inference_method}/{params_string}")
        else:
            mechanism_pth = Path(f"final_results/mechanisms/{mechanism}/{inference_method}/{params_string}")
        mechanism_pth.mkdir(parents=True, exist_ok=True)

        ### Inference Params 
        if inference_set != 'exhaustive' and comparison_set == 'exhaustive':
            raise ValueError('Cannot have exhaustive comparison without exhaustive inference.')
        
        if inference_set == 'exhaustive' and mechanism == 'rr':
            S_inputs = list(itertools.product([False,True], repeat=mechanism_params['n']))
            S_outputs = list(itertools.product([False,True], repeat=mechanism_params['n']))
        elif inference_set == 'exhaustive' and mechanism == 'above_threshold':
            S_inputs = list(itertools.product(list(range(mechanism_params['max_int_value']+1)), repeat=mechanism_params['list_length']))
            S_outputs = list(range(mechanism_params['list_length']+1))
        elif inference_set == 'min_representative' and mechanism == 'rr':
            S_inputs = list(itertools.product([False,True], repeat=mechanism_params['n']))
            S_outputs = [tuple([False]*mechanism_params['n'])]
        else: raise NotImplementedError(f'S_inf = {inference_method} not implemented for {mechanism}')


        ### File Params
        if not self.official:
            file_base = f'{inference_method}_{mechanism}_{params_string}_inf-{inference_set}_comp-{comparison_set}'
            stats_pth = Path(f"temp_results/stats/{inference_method}/inf-{inference_set}_comp-{comparison_set}/{mechanism}/{params_string}")
            stats_pth.mkdir(parents=True, exist_ok=True)
        else: 
            if self.get_examples:
                file_base = f'{inference_method}_{mechanism}_{params_string}_inf-{inference_set}_comp-{comparison_set}'
                stats_pth = Path(f"final_results/examples/{inference_method}/inf-{inference_set}_comp-{comparison_set}/{mechanism}/{params_string}")
                stats_pth.mkdir(parents=True, exist_ok=True)
            else:
                file_base = f'{inference_method}_{mechanism}_{params_string}_inf-{inference_set}_comp-{comparison_set}'
                stats_pth = Path(f"final_results/stats/{inference_method}/inf-{inference_set}_comp-{comparison_set}/{mechanism}/{params_string}")
                stats_pth.mkdir(parents=True, exist_ok=True)

        ### Scalability DF
        scalability_file = stats_pth / 'scalability.csv'
        scalability_df = pd.Series()

        ### Stats DF
        stats_file = stats_pth / 'stats.csv'
        stats_df = pd.Series()
        inference_probmat_file = stats_pth / 'inference_probmat.csv'
        unique_probs_file = stats_pth / 'unique_probs.csv'

        if mechanism == 'rr':
            self.__store_values(stats_df, 'N', mechanism_params['n'], stats_file)
            self.__store_values(stats_df, 'lambda', mechanism_params['lamb'], stats_file)
        elif mechanism == 'above_threshold':
            self.__store_values(stats_df, 'list_length', mechanism_params['list_length'], stats_file)
            self.__store_values(stats_df, 'max_int_value', mechanism_params['max_int_value'], stats_file)
            self.__store_values(stats_df, 'threshold', mechanism_params['threshold'], stats_file)
            self.__store_values(stats_df, 'lambda', mechanism_params['lamb'], stats_file)
        else: raise NotImplementedError(f'No stats initialization for {mechanism} mechanism')

        self.__store_values(stats_df, 'num_unique_probabilities', -1, stats_file)
        self.__store_values(stats_df, 'best_epsilon',-1, stats_file)
        self.__store_values(stats_df, 'worst_ratio', -1, stats_file)
        self.__store_values(stats_df, 'worst_assn', (None, None, None), stats_file)


        ### Logging Params
        # Initialize logger, from: https://stackoverflow.com/a/13733863
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        rootLogger = logging.getLogger()
        logs_pth = Path(f"logs")
        logs_pth.mkdir(parents=True, exist_ok=True)
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
        if mechanism == 'rr':
            mechanism_encoder = RandResponseEncoder(mechanism_params=mechanism_params,outfiles_dir=mechanism_pth)
        elif mechanism == 'above_threshold':
            mechanism_encoder = GeometricAboveEncoder(mechanism_params=mechanism_params,outfiles_dir=mechanism_pth)
        else: raise NotImplementedError

        # Encode and write files
        if inference_method == 'dice_flat' and inference_set == 'min_representative':
            # Give outputs as inputs because we will transpose later.
            mechanism_encoder.dice_flat_encoder(S_inputs=S_outputs)
        elif inference_method == 'dice_flat':
            mechanism_encoder.dice_flat_encoder(S_inputs=S_inputs)
        elif inference_method == 'direct' and mechanism == 'rr':
            # No encoding necessary for direct computation
            pass
        elif inference_method == 'storm':
            mechanism_encoder.storm_encoder(S_inputs=S_inputs, S_outputs=S_outputs)
        else: raise NotImplementedError

        self.__store_values(scalability_df,'file_write_time', time.time()-file_write_start, scalability_file)


        ##################
        # INFERENCE #
        ##################
        logging.info(f'\n\n-----------------------------------------------------------\n INFERENCE ({inference_method} {mechanism} {mechanism_params}) \n-----------------------------------------------------------\n')
        # Set up timeout for inference
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.timeout) 
        try:
            # Run inference based on chosen inference tool with specified inference set
            if inference_method == 'dice_flat' and inference_set == 'min_representative' and mechanism == 'rr':
                inference_timeseries, inference_probmat = inference.run_dice_rr_minimal(S_inputs=S_inputs,S_outputs=S_outputs,mechanism_filepath=mechanism_pth,stats_pth=stats_pth)
            elif inference_method == 'dice_flat':
                inference_timeseries, inference_probmat = inference.run_dice(S_inputs=S_inputs,S_outputs=S_outputs,mechanism_filepath=mechanism_pth,stats_pth=stats_pth)
                # NOTE: set Dice recursion limit appropriately for mechanism if not flat.
            elif inference_method == 'direct' and mechanism == 'rr':
                inference_timeseries, inference_probmat = inference.run_rr_direct(S_inputs=S_inputs,S_outputs=S_outputs,stats_pth=stats_pth,mechanism_params=mechanism_params)
            elif inference_method == 'storm' and mechanism == 'rr':
                inference_timeseries, inference_probmat = inference.run_storm_rr(S_inputs=S_inputs,S_outputs=S_outputs,mechanism_filepath=mechanism_pth, stats_pth=stats_pth,mechanism_params=mechanism_params)
            else: raise NotImplementedError
            # disable timeout
            signal.alarm(0)

            # Gather stats
            probmat_df = pd.DataFrame(inference_probmat)
            unique_probs = np.unique(probmat_df)
            probmat_df.to_csv(inference_probmat_file)
            del(probmat_df)

            self.__store_values(stats_df, 'num_unique_probabilities', len(unique_probs), stats_file)
            self.__store_values(scalability_df, 'total_inference_time',inference_timeseries.sum(), scalability_file)
            self.__store_values(scalability_df, 'mean_inf_time_per_call',inference_timeseries.mean(), scalability_file)
            self.__store_values(scalability_df, 'num_inference_calls',inference_timeseries.count(), scalability_file)

            # Save stats files
            pd.Series(unique_probs).to_csv(unique_probs_file)
            stats_df.to_csv(stats_file)

        except TimeoutError:
            self.__store_values(scalability_df, 'total_inference_time',f"TIMEOUT ({self.timeout} seconds)", scalability_file)
            self.__store_values(scalability_df, 'mean_inf_time_per_call',f"TIMEOUT ({self.timeout} seconds)", scalability_file)
            self.__store_values(scalability_df, 'num_inference_calls',f"TIMEOUT ({self.timeout} seconds)", scalability_file)
            stats_df.to_csv(stats_file)
            timed_out = True





        ################
        # VERIFICATION #
        ################
        logging.info(f'\n\n-----------------------------------------------------------\n VERIFICATION ({inference_method} {mechanism} {mechanism_params}) \n-----------------------------------------------------------\n')


        if not timed_out:
            start_verification = time.time()

            # Optionally enumerate all instantiations and their privacy bounds
            if self.get_examples:
                comparison.get_examples_rr2n(mechanism_params['n'], inference_probmat=inference_probmat,examples_file=(stats_pth / 'examples.csv'))
                print("got examples!")
                exit(0)
            # Compute bound based on specified privacy set. 
            elif comparison_set == 'exhaustive':
                worst_assn, worst_ratio = comparison.run_exhaustive(S_inputs=S_inputs,S_outputs=S_outputs,inference_probmat=inference_probmat,mechanism=mechanism,mechanism_params=mechanism_params)
            elif comparison_set == 'rr_2n':
                if mechanism != 'rr':
                    raise ValueError('rr_2n comparison method is only for RR mechansim')
                worst_assn, worst_ratio = comparison.run_rr_2n(mechanism_params['n'],inference_probmat=inference_probmat)
            else: NotImplementedError

            # Store stats
            self.__store_values(scalability_df, 'verification_time', time.time() - start_verification, scalability_file)
            best_epsilon = math.log(worst_ratio)
            logging.info(f'\nBest param is {best_epsilon}-Differential Privacy for {mechanism} {mechanism_params}\nPr[A(x)=y]/Pr[A(x\')=y] = {worst_ratio} for Worst Case Assignment: (x,x\',y) = {worst_assn}.\n')
            self.__store_values(stats_df, 'best_epsilon', best_epsilon, stats_file)
            self.__store_values(stats_df, 'worst_ratio', worst_ratio, stats_file)
            self.__store_values(stats_df, 'worst_assn', worst_assn, stats_file)
            total_duration = time.time() - total_start_time
            total_experiment_time = scalability_df['file_write_time'] + scalability_df['total_inference_time'] + scalability_df['verification_time']
            self.__store_values(scalability_df, 'total_experiment_time', total_experiment_time, scalability_file)
            self.__store_values(scalability_df, 'total_duration', total_duration, scalability_file)
            self.__store_values(scalability_df, 'python_misc_time', total_duration - total_experiment_time, scalability_file)
    
    def __store_values(self, df, key, value, pth):
        df.at[key] = value
        df.to_csv(pth)
