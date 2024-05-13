import pandas as pd
import time
import json
import subprocess
from pathlib import Path
import os
import stormpy
import stormpy.pars
import re

unstringify = {'false': False, 'true': True}
stringify = {True:'true',False:'false'}
binify = {True:'1',False:'0'}

def __dice_subprocess(mechanism_file, assn, output_distr):
    start_dice = time.time()
    try:
        proc = subprocess.Popen(f"../../../dice/_build/install/default/bin/dice {mechanism_file} -json -recursion-limit 1 -wmc-type 0 -show-size -inline-functions", shell=True, stdout=subprocess.PIPE)
        output = proc.stdout.read()
    except KeyboardInterrupt:
        proc.kill()
        raise
    except TimeoutError:
        proc.kill()
        raise

    dice_time = time.time() - start_dice
    result = json.loads(output.decode('utf-8'))
    del(output)

    if 'count' in str(mechanism_file):
        for res in result[0]['Joint Distribution'][1:]:
            output_distr[(f'{res[0]}',)] = float(res[1])
    else:
        for res in result[0]['Joint Distribution'][-2**len(assn):]:
            if 'max_int_value' in str(mechanism_file):
                distr = tuple(val for val in res[0].replace('\'','').replace('(','').replace(')','').replace(' ','').split(','))
                output_distr[distr] = res[1]
            else:
                distr = tuple(unstringify[val] for val in res[0].replace('\'','').replace('(','').replace(')','').replace(' ','').split(','))
                output_distr[distr] = res[1]
            # Clean up
            del(res)
            del(distr)

    bdd_size = int(result[1]['Final compiled BDD size'])
    
    return dice_time, output_distr, bdd_size

def __make_files(stats_pth):
    inference_timemat_file = stats_pth / 'timemat.csv'
    bdd_sizes_file = stats_pth / 'bdd_sizes.csv'
    return inference_timemat_file, bdd_sizes_file

def __find_mechanism_file(mechanism_filepath, assn):
    if 'max_int_value' not in str(mechanism_filepath):
        assn_abbrev = ''.join([stringify[a] for a in assn])
    else:
        assn_abbrev = ''.join([str(a) for a in assn])
    mechanism_file = mechanism_filepath / f'{assn_abbrev}.dice'
    return mechanism_file

def run_rr_direct(S_inputs,S_outputs,stats_pth,mechanism_params):
    inference_probmat = {x:{} for x in S_inputs}
    inference_timeseries = pd.Series([None]*(len(S_inputs)*len(S_outputs)))
    i = 0
    inference_timemat_file, _ = __make_files(stats_pth)
    for x in S_inputs:
        for y in S_outputs:
            start = time.time()
            pairwise_eq = [xi == yi for (xi,yi) in zip(x,y)]
            num_flips = pairwise_eq.count(False)
            num_no_flips = pairwise_eq.count(True)
            inference_probmat[x][y] = (mechanism_params['lamb']**num_flips) * ((1-mechanism_params['lamb'])**num_no_flips)
            inference_timeseries[i] = time.time() - start
            i += 1
            inference_timeseries.to_csv(inference_timemat_file)
    return inference_timeseries, inference_probmat

def run_dice(S_inputs, S_outputs, mechanism_filepath, stats_pth):
    inference_timemat_file, bdd_sizes_file = __make_files(stats_pth)

    inference_probmat = {}
    inference_timeseries = pd.Series({x: 0 for x in S_inputs})
    bdd_sizes = pd.Series({x: -1 for x in S_inputs})

    # Run dice on each file (one file per input assignment)
    for input in S_inputs:
        output_distr = {}
        mechanism_file = __find_mechanism_file(mechanism_filepath, input)

        # Run Inference
        dice_time, output_distr, bdd_size = __dice_subprocess(mechanism_file, input, output_distr=output_distr)
        inference_timeseries[input] = dice_time
        inference_probmat[input] = output_distr
        bdd_sizes[input] = bdd_size

        # Save stats files
        inference_timeseries.to_csv(inference_timemat_file)
        bdd_sizes.to_csv(bdd_sizes_file)
    return inference_timeseries, inference_probmat

def run_dice_rr_minimal(S_inputs, S_outputs, mechanism_filepath, stats_pth):
    assn = S_inputs[0]
    inference_timemat_file, bdd_sizes_file = __make_files(stats_pth)
    mechanism_file = __find_mechanism_file(mechanism_filepath, assn)
    output_distr = {k: None for k in S_outputs}

    # Run dice on just one input
    dice_time, output_distr, bdd_size = __dice_subprocess(mechanism_file, assn, output_distr=output_distr)
    inference_timeseries = pd.Series([dice_time])

    # Gather results
    bdd_sizes = pd.Series([bdd_size])

    # transpose results
    target_out = tuple(False for _ in range(len(assn)))
    inference_probmat = {tuple(key) : {target_out: output_distr[key]} for key in output_distr}
    del(output_distr)

    # Save stats files  
    inference_timeseries.to_csv(inference_timemat_file)
    bdd_sizes.to_csv(bdd_sizes_file)

    return inference_timeseries, inference_probmat

def run_storm_rr(S_inputs,S_outputs,mechanism_filepath,stats_pth,mechanism_params,timeout=1200):
    inference_probmat = {x:{y: -1. for y in S_outputs} for x in S_inputs}
    inference_timeseries = {}
    stats_file = stats_pth / 'model_stats.csv'
    props_file = stats_pth / 'props.csv'
    stats = pd.Series()
    props = [None for _ in S_outputs]

    model_stats = False
    runs = 0
    prism_program = stormpy.parse_prism_program(str(mechanism_filepath / 'model.pm'))
    for i,output in enumerate(S_outputs):
        prop_val = ' & '.join([f'y{i+1} = {binify[v]}' for i,v in enumerate(output)])
        prop = f'P=? [F {prop_val}]'
        props[i] = prop
        
        model_build_start = time.time()
        properties = stormpy.parse_properties(prop, prism_program)
        model = stormpy.build_parametric_model(prism_program, properties)
        inference_timeseries['model_build'] = time.time() - model_build_start

        if not model_stats:
            stats['num_states'] = model.nr_states
            stats['num_trans'] = model.nr_transitions
            model_stats = True
        parameters = model.collect_probability_parameters()
        for input in S_inputs:
            inst = {}
            for x in parameters:
                if x.name == 'lamb':
                    # Set lambda, this will stay unset if we are doing parametric model checking
                    inst[x] = stormpy.RationalRF(mechanism_params['lamb'])
                elif 'p' in x.name:
                    # Find probability parameter index NOTE: check how long this is taking...
                    i = int(re.findall('\d+', x.name)[0])

                    # Set probability parameter at index i-1 to value
                    inst[x] = stormpy.RationalRF(binify[input[i-1]])

            stormpy_start = time.time()
            instantiator = stormpy.pars.PDtmcInstantiator(model)
            instantiated_model = instantiator.instantiate(inst)
            result = stormpy.model_checking(instantiated_model, properties[0])
            stormpy_time = time.time() - stormpy_start
            # Clean up memory
            del(inst)
            del(instantiated_model)
            del(instantiator)
            runs += 1

            inference_probmat[input][output] = result.at(0)
            del(result)

            assn_str = ''.join([f'{binify[input[i]]}-{binify[output[i]]}' for i in range(len(output))])
            inference_timeseries[assn_str] = stormpy_time
            del(assn_str)

        # Clean up memory
        del(properties)
        del(model)
        del(parameters)

    stats['runs'] = runs
    stats.to_csv(stats_file)
    pd.Series(props).to_csv(props_file)
    return pd.Series(inference_timeseries.values()),inference_probmat
