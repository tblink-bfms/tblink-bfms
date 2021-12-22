'''
Created on Oct 29, 2021

@author: mballance
'''
from _io import StringIO

from tblink_bfms.generators.gen_base import GenBase
from tblink_bfms.generators.gen_sv import GenSv
from tblink_bfms.generators.gen_sv_bfm_impl import GenSvBfmImpl
from tblink_rpc_utils.gen_utils import GenUtils
from tblink_rpc_utils.output import Output


class GenSystemVerilog(GenBase):
    
    def __init__(self):
        self.kind_m = {
            "bfm" : GenSvBfmImpl().gen,
            "define_type": GenSv().gen_define_type,
            "method_t.decl" : GenSv().gen_method_t_decl,
            "method_t.find" : GenSv().gen_method_t_find,
            "method_t.impl" : GenSv().gen_method_t_impl,
            "invoke_nb" : GenSv().gen_invoke_nb,
            "invoke_b" : GenSv().gen_invoke_b,
            }

    def tblink_gen(self, iftype, is_mirror, kind=None, **kwargs):
        ret_s = StringIO()
        out = Output(ret_s)
        
        if kind is None:
            raise Exception("Kind must be specified")
        
        if kind not in self.kind_m.keys():
            raise Exception("Kind %s not supported" % kind)
        
        if "ind" in kwargs.keys():
            out.ind = kwargs["ind"]

        self.kind_m[kind](out, iftype, is_mirror, **kwargs)

        return ret_s.getvalue()
    

        
