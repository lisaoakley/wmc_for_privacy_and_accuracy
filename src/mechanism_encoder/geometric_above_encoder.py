from .mechanism_encoder import MechanismEncoder
import math

class GeometricAboveEncoder(MechanismEncoder):
    def __init__(self, mechanism_params, outfiles_dir):
        self.params = mechanism_params
        self.outfiles_dir = outfiles_dir

    def __gen_discrete_str(self,center):

        # initialize things
        max_int_val = self.params['max_int_value'] # cutoff
        s = self.params['lamb']
        # We want an entry for all int values 0,1,2,..,max_int_val
        vals = [0] * (max_int_val+1)
        
        # Get center probability
        # f(z) = (e^((1/s))-1)/(e^(1/s)+1) * e^(-|z-c|)/s
        vals[center] = (math.e**((1/s))-1)/(math.e**(1/s)+1)
        single_tail_val = (1 - vals[center])/2

        # RHS
        rhs_total = 0
        # Treat everything between (center,max_val) the same
        for i in range(center+1,max_int_val):
            vals[i] = ((math.e**((1/s))-1)/(math.e**(1/s)+1)) * math.e**(-abs(i-center)/s)
            rhs_total += vals[i] 
        # rest of tail density on last element
        vals[max_int_val] += single_tail_val - rhs_total

        # LHS
        lhs_total = 0
        # Treat everything between (0,center) the same
        for i in range(1,center):
            vals[i] = ((math.e**((1/s))-1)/(math.e**(1/s)+1)) * math.e**(-abs(i-center)/s)
            lhs_total += vals[i] 
        # rest of the tail density on the first element
        vals[0] += single_tail_val - lhs_total

        return ','.join([str(v) for v in vals])


    def dice_flat_encoder(self, S_inputs):
        int_size = int(self.params['list_length']).bit_length() # get the int size needed to encode something at index list_length
        for arr in S_inputs:
            threshold_let_statement = f"let t_noisy = discrete({self.__gen_discrete_str(center=self.params['threshold'])}) in\n"
            elements_let_statements = ''.join([f'let x{i}_noisy = discrete({self.__gen_discrete_str(center=val)}) in\n' for i,val in enumerate(arr)])
            # If one of the noisy elements is greater than the noisy threshold, return that element, otherwise, return index "list_length"
            first_comparison_let_statement = f"let answ = if x0_noisy > t_noisy then int({int_size},0) else int({int_size},{self.params['list_length']}) in\n" # the element at index "n" or "list_length" does not exist, this indicates that the threshold was not breached
            comparisons_let_statements = ''.join([f"let answ = if answ == int({int_size},{self.params['list_length']}) && x{i}_noisy > t_noisy then int({int_size},{i}) else answ in\n" for i,val in enumerate(arr)])
            
            end = "answ"
            program = f'{threshold_let_statement}{elements_let_statements}{first_comparison_let_statement}{comparisons_let_statements}{end}'

            assn_abbrev = ''.join([str(a) for a in arr])
            with open(self.outfiles_dir / f'{assn_abbrev}.dice', "w") as f:
                f.write(program)
