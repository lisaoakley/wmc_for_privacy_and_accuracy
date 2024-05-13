from .mechanism_encoder import MechanismEncoder
import itertools

class RandResponseEncoder(MechanismEncoder):
    def __init__(self, mechanism_params, outfiles_dir):
        super().__init__(mechanism_params,outfiles_dir)
        self.lamb = mechanism_params['lamb']
        self.n = mechanism_params['n']

    def storm_encoder(self, S_inputs, S_outputs):
        ## All string generation
        initial_state_probs = '\n'.join([f'const double p{i+1};' for i in range(self.n)])
        client_copies = '\n'.join([f'module client{i+1} = client1 [ x1=x{i+1}, y1=y{i+1}, p1=p{i+1}, x1_set=x{i+1}_set] endmodule' for i in range(1,self.n)])
        with open(self.outfiles_dir / f'model.pm', "w") as file1:
            # Writing data to a file
            file1.write(f"""dtmc

// privacy parameter
const double lamb;   
{initial_state_probs}
// num clients
const N={self.n};

// base client def
module client1
    // client true bit
    x1 : [-1..1];
    y1 : [-1..1];
    x1_set : bool init false;

    // set x1 as 1 if p1=1 and x1 as 0 if p1=0
    [] !x1_set -> p1 : (x1' = 1) & (x1_set'=true) + 1-p1 : (x1' = 0) & (x1_set'=true);


    // if x=0, transition probabilities for y1 vals
    [] x1=0 & y1=-1 & x1_set -> (lamb) : (y1'=1)
                + (1-lamb) : (y1'=0);

    // if x=1, transition probabilities for y1 vals (symmetric)
    [] x1=1 & y1=-1 & x1_set -> (1-lamb) : (y1'=1) 
                + (lamb) : (y1'=0);
endmodule
    

// same probabilities for other clients.
{client_copies}
""")

    def dice_flat_encoder(self, S_inputs):
        # Generate a flat version of the program (no function calls, no free variables)
        # This should make things run way faster.
        for assn in S_inputs:
            let_statements = ''.join([f'let r{i} = if flip {self.lamb} then {self.stringify[not val]} else {self.stringify[val]} in\n' for i,val in enumerate(assn)])
            nested_tuple_left = ''.join([f'(r{i},' for i in range(len(assn)-1)])
            nested_tuple_right = ')' * (len(assn)-1)
            program = f'{let_statements}{nested_tuple_left}r{len(assn)-1}{nested_tuple_right}'

            assn_abbrev = ''.join([self.stringify[a] for a in assn])
            with open(self.outfiles_dir / f'{assn_abbrev}.dice', "w") as f:
                f.write(program)