from .mechanism_encoder import MechanismEncoder

class RandResponseCountEncoder(MechanismEncoder):
    def __init__(self, mechanism_params, outfiles_dir):
        super().__init__(mechanism_params,outfiles_dir)
        self.lamb = mechanism_params['lamb']
        self.n = mechanism_params['n']

    def dice_flat_encoder(self, S_inputs):
        # Generate a flat version of the program (no function calls, no free variables)
        # This should make things run way faster.
        for assn in S_inputs:
            # pad with zeros because of Dice bug (need n+1 total buckets in discrete so int sizes match up)
            padding = ', '.join(['0']*(len(assn)-1))
            let_statements = ''.join([f'let r{i} = discrete({self.lamb if val else 1-self.lamb}, {1-self.lamb if val else self.lamb}, {padding}) in\n' for i,val in enumerate(assn)])
            sum_statement = '+'.join([f'r{i}' for i in range(len(assn))])
            program = f'{let_statements}{sum_statement}'

            assn_abbrev = ''.join([self.stringify[a] for a in assn])
            with open(self.outfiles_dir / f'{assn_abbrev}.dice', "w") as f:
                f.write(program)

    def non_private_query(self, x):
        return x.count(True)