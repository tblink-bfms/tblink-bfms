'''
Created on Oct 29, 2021

@author: mballance
'''
from tblink_bfms.generators.gen_base import GenBase

class GenVerilog(GenBase):
    
    
    def tblink_gen(self, iftype, is_mirror, kind=None, **kwargs):
        return "gen_verilog"