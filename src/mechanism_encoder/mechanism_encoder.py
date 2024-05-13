class MechanismEncoder(object):
    def __init__(self, mechanism_params, outfiles_dir):
        self.params = mechanism_params
        self.outfiles_dir = outfiles_dir
        self.stringify = {True:'true',False:'false'}
        self.binify = {True:'1',False:'0'}

    def storm_encoder(self, S_inputs, S_outputs):
        """
        Makes all the Storm (DTMC model checker) program files for specified mechanism, input, and output
        """
        raise NotImplementedError
        
    def dice_flat_encoder(self, S_inputs):
        """
        This encoder makes many flat files
        """
        raise NotImplementedError
    
    def sexp_formula_encoder(self):
        raise NotImplementedError
    
    def non_private_query(self,x):
        """
        Runs the query for specific input and gives the non-noisy result
        """
        raise NotImplementedError
