import pandas as pd

def __calc_eps_DP_ratio(input, neighbor, output, inference_probmat,mechanism=None):
    if mechanism == 'above_threshold':
        output = (f'{output}',)
        return float(inference_probmat[input][output]) / float(inference_probmat[neighbor][output])
    else:
        return float(inference_probmat[input][output]) / float(inference_probmat[neighbor][output])
    
def __make_neighbors(input, i, mechanism, mechanism_params):
    if mechanism == 'rr':
        # only need to flip one bit to make a neighbor
        return [tuple(not input[j] if i == j else input[j] for j in range(len(input)))]
    elif mechanism == 'above_threshold':
        # Need one above and one below
        neighbors = []
        if input[i] < mechanism_params['max_int_value']:
            n1 = tuple(input[j]+1 if i == j else input[j] for j in range(len(input)))
            neighbors.append(n1)
        if input[i] > 0:
            n2 = tuple(input[j]-1 if i == j else input[j] for j in range(len(input)))
            neighbors.append(n2)
        return neighbors
    else: raise NotImplementedError

def run_exhaustive(S_inputs, S_outputs, inference_probmat, mechanism='rr',mechanism_params=[]):
    # Iterate through all input assignments
    worst_assn = (None, None, None)
    worst_ratio = -1

    for input in S_inputs:
        # flip each element of assignment to create neighbor
        for i in range(len(input)):
            neighbors = __make_neighbors(input, i, mechanism, mechanism_params)    
            # check DP ratio for each output, keep largest
            for output in S_outputs:
                for neighbor in neighbors:
                    ratio = __calc_eps_DP_ratio(input, neighbor, output, inference_probmat,mechanism)
                    if ratio > worst_ratio:
                        worst_ratio = ratio
                        worst_assn = (input, neighbor, output)


    return worst_assn, worst_ratio

def __gen_neighbors(assignments, n):
    # generate correct input/neighbor pairs
    for i in range(n+1):
        input = tuple([True if j < i else False for j in range(n)])
        if i == 0:
            neighbor = tuple([True if j < i+1 else False for j in range(n)])
            assignments[0] = (input, neighbor)
        elif i == n:
            neighbor = tuple([True if j < i-1 else False for j in range(n)])
            assignments[-1] = (input, neighbor)
        else:
            neighbor1 = tuple([True if j < i-1 else False for j in range(n)])
            neighbor2 = tuple([True if j < i+1 else False for j in range(n)])
            assignments[2*i-1] = (input, neighbor1)
            assignments[2*i] = (input, neighbor2)
    return assignments

def run_rr_2n(n, inference_probmat):
    worst_assn = (None, None, None)
    worst_ratio = -1
    assignments = [None] * (2*n)
    output = tuple([False] * n)

    assignments = __gen_neighbors(assignments=assignments,n=n)
    
    # run through all assignments
    for assn in assignments:
        input = assn[0]
        neighbor = assn[1]

        ratio = __calc_eps_DP_ratio(input, neighbor, output, inference_probmat)
        if ratio > worst_ratio:
            worst_ratio = ratio
            worst_assn = (input, neighbor, output)

    return worst_assn, worst_ratio

def get_examples_rr2n(n, inference_probmat,examples_file):
    assignments = [None] * (2*n)
    output = tuple([False] * n)
    examples = pd.DataFrame(index=range(len(assignments)), columns=['$e^\epsilon$','Neighbor 1', 'Neighbor 2', 'Output'])

    assignments = __gen_neighbors(assignments=assignments,n=n)

    # run through all assignments
    for i,assn in enumerate(assignments):
        input = assn[0]
        neighbor = assn[1]

        ratio = __calc_eps_DP_ratio(input, neighbor, output, inference_probmat)
        examples.loc[i,'$e^\epsilon$'] = ratio
        examples.loc[i,'Neighbor 1'] = input
        examples.loc[i,'Neighbor 2'] = neighbor
        examples.loc[i,'Output'] = output

    examples = examples.sort_values('$e^\epsilon$')
    examples.to_csv(examples_file)