from math import floor,ceil
import pandas as pd

def run_accuracy(S_inputs, inference_probmat, alpha, mechanism_encoder):
    err = float('inf')
    bounding_assn = ()
    for input in S_inputs:
        true_val = mechanism_encoder.non_private_query(input)
        rng = [val 
               for val in range(true_val-ceil(alpha),true_val+floor(alpha)+1) 
               if val >=0 and val <= len(input)]
        new_err = sum([inference_probmat[input][(f'{output}',)] for output in rng])
        if err > new_err:
            err = new_err
            bounding_assn = input
        
    return err, bounding_assn
        

def get_examples(S_inputs, inference_probmat, alpha, mechanism_encoder, examples_file):
    examples = pd.DataFrame(index=range(len(S_inputs)), columns=['$1-\\beta$','Input'])

    for i,input in enumerate(S_inputs):
        true_val = mechanism_encoder.non_private_query(input)
        rng = [val 
               for val in range(true_val-ceil(alpha),true_val+floor(alpha)+1) 
               if val >=0 and val <= len(input)]
        examples.loc[i,'$1-\\beta$'] = sum([inference_probmat[input][(f'{output}',)] for output in rng])
        examples.loc[i,'Input'] = ''.join(['1' if j else '0' for j in input])

    examples = examples.sort_values('$1-\\beta$',ascending=False)
    examples.to_csv(examples_file)