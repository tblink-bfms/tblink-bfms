'''
Created on Oct 29, 2021

@author: mballance
'''
from tblink_bfms.generators.gen_base import GenBase
from _io import StringIO
from tblink_rpc.output import Output
from tblink_rpc.gen_utils import GenUtils

class GenSystemVerilog(GenBase):
    

    def tblink_gen(self, iftype, is_mirror, kind=None, **kwargs):
        ret_s = StringIO()
        out = Output(ret_s)

        # Pretty much all output goes at one indent level         
        out.inc_ind()
        
        out.println("string m_inst_name;")
        out.println()
        out.println("function string inst_name();")
        out.inc_ind()
        out.println("return m_inst_name;")
        out.dec_ind()
        out.println("endfunction")
        out.println()
        
        self.gen_define_type(out, iftype)
        
        out.dec_ind()
        out.println("`ifndef VERILATOR")
        out.inc_ind()
        self.gen_stdsv_impl(out, iftype, is_mirror)
        out.dec_ind()
        out.println("`else // ifndef VERILATOR")
        out.inc_ind()
        self.gen_dpisv_impl(out, iftype, is_mirror)
        out.dec_ind()
        out.println("`endif // ifndef VERILATOR")
        out.inc_ind()

        return ret_s.getvalue()
    
    def gen_define_type(self, out, iftype):
        g_util = GenUtils(cpp_ptr=False)
        out.println("function automatic tblink_rpc::IInterfaceType define_type(tblink_rpc::IEndpoint ep);")
        out.inc_ind()
        out.println("tblink_rpc::IInterfaceType iftype;")
        out.println()
        out.println("iftype = ep.findInterfaceType(string'(\"%s\"));" % iftype.name)
        out.println()
        out.println("if (iftype == null) begin")
        out.inc_ind()
        
        out.println("tblink_rpc::IInterfaceTypeBuilder iftype_b = ep.newInterfaceTypeBuilder(")
        out.inc_ind()
        out.println("string'(\"%s\"));" % iftype.name)
        out.dec_ind()

        out.println("tblink_rpc::IMethodTypeBuilder mtb;")

        for i,m in enumerate(iftype.methods):
            out.println("mtb = iftype_b.newMethodTypeBuilder(")
            out.inc_ind()
            out.println("string'(\"%s\")," % m.name)
            out.println("%d,  // method id" % i)
            out.println("%s,  // return type" % g_util.gen_mk_type("iftype_b", m.rtype))
            out.println("%s,  // is-export" % g_util.bool_str(m.is_export))
            out.println("%s); // is-blocking" % g_util.bool_str(m.is_blocking))
            out.dec_ind()
            
            for p in m.params:
                out.write("%smtb.add_param(string'(\"%s\"), " %(
                    out.ind,
                    p[0]))
                out.write("%s);" % g_util.gen_mk_type("iftype_b", p[1]))
            
            out.println("void'(iftype_b.add_method(mtb));")
            out.println()
                
        out.println()
        out.println("iftype = ep.defineInterfaceType(iftype_b);")

        out.dec_ind()
        out.println("end")

        out.println("return iftype;")        
        out.dec_ind()
        out.println("endfunction")
        out.println()
        
    def gen_stdsv_impl(self, out, iftype, is_mirror):
        g_util = GenUtils(cpp_ptr=False)
        
        out.println("interface %s_core();" % g_util.to_id(iftype.name))
        out.inc_ind()
        out.println("import tblink_rpc::*;")
        out.println("IInterfaceInst ifinst;")
        out.println()
        out.println("typedef virtual %s_core vif_t;" % g_util.to_id(iftype.name))
        out.println()
        out.println("function automatic IParamVal invoke_nb(")
        out.inc_ind()
        out.println("input IInterfaceInst         ifinst,")
        out.println("input IMethodType            method,")
        out.println("input IParamValVec           params);")
        out.dec_ind()
        out.println("endfunction")
        out.println()
        
        out.dec_ind()
        out.println("endinterface")
        out.println()

        out.println("%s_core u_core();" % g_util.to_id(iftype.name))
        out.println()
        
        out.println("initial begin")
        out.inc_ind()
        out.println("m_inst_name = $sformatf(\"%m\");")
        out.println("u_core.init(")
        out.inc_ind()
        out.println("m_inst_name,")
        out.println("u_core);")
        out.dec_ind()
        out.println("tblink_rpc::tblink_rpc_start();")
        
        out.dec_ind()
        out.println("end")
        pass
    
    def gen_dpisv_impl(self, out, iftype, is_mirror):
        g_util = GenUtils(cpp_ptr=False)
        out.println("function automatic chandle %s_core_invoke_nb(" % (
            g_util.to_id(iftype.name),))
        out.inc_ind()
        out.inc_ind()
        out.println("chandle ifinst_h,")
        out.println("chandle method_h,")
        out.println("chandle params_h);")
        out.dec_ind()
        out.println("tblink_rpc::DpiInterfaceInst ifinst = new(ifinst_h);")
        out.println("tblink_rpc::DpiMethodType method = new(method_h);")
        out.println("tblink_rpc::DpiParamValVec params = new(params_h);")
        out.println("tblink_rpc::IParamVal retval;")
        out.println("chandle retval_h;")
        out.println("longint id = method.id();")
        out.println()
        out.println("case (id)")
        for i,m in enumerate(iftype.methods):
            
            if not m.is_blocking and ((not is_mirror and m.is_export) or (is_mirror and not m.is_export)):
                out.println("%d: begin // %s" % (i, m.name))
                out.inc_ind()
                out.dec_ind()
                out.println("end")
                out.println()
        out.println("default:")
        out.inc_ind()
        out.println("$display(\"TbLink Error: %%m - unknown method id %%0d\", id);")
        out.println("$stop;")
        out.dec_ind()
        out.println("endcase")

        out.dec_ind()
        out.println("endfunction")
        pass
        