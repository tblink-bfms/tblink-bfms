'''
Created on Oct 29, 2021

@author: mballance
'''
from tblink_bfms.generators.gen_base import GenBase
from tblink_bfms.generators.gen_systemverilog import GenSystemVerilog
from tblink_bfms.generators.gen_verilog import GenVerilog


class GenRgy(object):
    
    _inst = None
    
    def __init__(self):
        self.gen_m = {}
        
        self.gen_m["tblink.bfm_impl.sv"] = GenSystemVerilog
        self.gen_m["tblink.bfm_impl.vl"] = GenVerilog
        pass
    
    def find_gen(self, gen_t):
        if gen_t in self.gen_m.keys():
            return self.gen_m[gen_t]
        else:
            return None

    @classmethod    
    def inst(cls):
        if cls._inst is None:
            cls._inst = GenRgy()
        return cls._inst
    
    