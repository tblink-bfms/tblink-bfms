'''
Created on Oct 29, 2021

@author: mballance
'''
from _io import StringIO

from tblink_bfms.generators.gen_base import GenBase
from tblink_rpc_utils.gen_utils import GenUtils
from tblink_rpc_utils.output import Output


class GenVerilog(GenBase):
    
    def __init__(self):
        self.kind_m = {
            "bfm" : self.gen_bfm
        }
        
    def gen_bfm(self, out, iftype, is_mirror, **kwargs):

        out.inc_ind()        
        self.gen_fields(out, iftype, is_mirror)
        out.dec_ind()
        out.println()
        
        # TODO: generate functions
        
        # generate define-type
        out.inc_ind()
        self.gen_define_type(out, iftype)
        out.dec_ind()
        
        
        out.println("initial begin")
        out.inc_ind()
        out.println("m_ep = $tblink_rpc_ITbLink_get_default_ep;")
        out.println()
        out.println("if (m_ep == 0) begin")
        out.inc_ind()
        out.println("$display(\"TbLink Error: no default endpoint created\");")
        out.println("$finish(1);")
        out.dec_ind()
        out.println("end")
        out.println()
        out.println("m_iftype = define_type(m_ep);")
        
        out.println()
        out.println("// TODO: method-lookup")
        out.println()
        out.println("// TODO: event-processing loop")
        out.dec_ind()
        out.println("end")
        pass
    
    def gen_fields(self, out, iftype, is_mirror):
        # TODO: generate fields
        # - event
        # - ep_h
        # - iftype_h
        # - ifinst_h
        # - method handles
        out.println("`ifdef IVERILOG")
        out.inc_ind()
        out.println("event m_ev;")
        out.dec_ind()
        out.println("`else")
        out.inc_ind()
        out.println("reg m_ev = 0;")
        out.dec_ind()
        out.println("`endif")
        
        out.inc_ind()
        out.println("reg[63:0]    m_ep     = 0;")
        out.println("reg[63:0]    m_iftype = 0;")
        out.println("reg[63:0]    m_ifinst = 0;")
        for m in iftype.methods:
            if not m.is_export and not is_mirror or m.is_export and is_mirror:
                out.println("reg[63:0]    m_%s;" % m.name)
        out.dec_ind()
        pass
    
    def gen_define_type(self, out, iftype):
        g_util = GenUtils(vlog=True)
        out.println("function reg[63:0] define_type(input reg[63:0] ep);")
        out.inc_ind()
        out.println("reg[63:0] iftype;")
        out.println("reg[63:0] method;")
        out.println("reg[63:0] iftype_b;")
        out.println("reg[63:0] mtb;")
        out.dec_ind()
        out.println("begin")
            
        out.inc_ind()
        out.println()
        out.println("iftype = $tblink_rpc_IEndpoint_findInterfaceType(ep, \"%s\");" % iftype.name)
        out.println()
        out.println("if (iftype == 0) begin")
        out.inc_ind()
        
        out.println("iftype_b = $tblink_rpc_IEndpoint_newInterfaceTypeBuilder(")
        out.inc_ind()
        out.println("ep,")
        out.println("\"%s\");" % iftype.name)
        out.dec_ind()
        out.println("$display(\"iftype_b: 'h%08h\", iftype_b);")

        for i,m in enumerate(iftype.methods):
            out.println("mtb = $tblink_rpc_IInterfaceTypeBuilder_newMethodTypeBuilder(")
            out.inc_ind()
            out.println("iftype_b,")
            out.println("\"%s\"," % m.name)
            out.println("%d,  // method id" % i)
            out.println("%s,  // return type" % g_util.gen_mk_type("iftype_b", m.rtype))
            out.println("%s,  // is-export" % g_util.bool_str(m.is_export))
            out.println("%s); // is-blocking" % g_util.bool_str(m.is_blocking))
            out.dec_ind()
        
            for p in m.params:
                out.write("%s$tblink_rpc_IMethodTypeBuilder_add_param(mtb, \"%s\", " %(
                    out.ind,
                    p[0]))
                out.write("%s);\n" % g_util.gen_mk_type("iftype_b", p[1]))
        
            out.println("method = $tblink_rpc_IInterfaceTypeBuilder_add_method(iftype_b, mtb);")
            out.println()
                
        out.println()
        out.println("iftype = $tblink_rpc_IEndpoint_defineInterfaceType(ep, iftype_b);")

        out.dec_ind()
        out.println("end")

        out.println("define_type = iftype;")        
        out.dec_ind()
        out.println("end")
        out.println("endfunction")
        out.println()        
    
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
    