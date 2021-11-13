'''
Created on Nov 12, 2021

@author: mballance
'''
from tblink_rpc.gen_utils import GenUtils
from tblink_rpc.output import Output
from tblink_bfms.generators.gen_sv import GenSv


class GenSvBfmImpl(object):
    
    def gen(self, out, iftype, is_mirror, **kwargs):
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

        GenSv(is_automatic=True).gen_define_type(out, iftype, is_mirror)
        
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
        
    def gen_stdsv_impl(self, out, iftype, is_mirror):
        g_util = GenUtils(cpp_ptr=False)
        
        out.println("interface %s_core();" % g_util.to_id(iftype.name))
        out.inc_ind()
        out.println("import tblink_rpc::*;")
        out.println("IInterfaceInst ifinst;")
        out.println()
        out.println("typedef virtual %s_core vif_t;" % g_util.to_id(iftype.name))
        out.println()
        out.println("function automatic void init(")
        out.inc_ind()
        out.inc_ind()
        out.println("string inst_name,")
        out.println("vif_t vif);")
        out.dec_ind()
        
        out.println("TbLink tblink = TbLink::inst();")
        out.println("IEndpoint ep;");
        out.println("IInterfaceType iftype;")
        out.println("SVInterfaceImplVif #(vif_t) ifimpl;")
        out.println()
        out.println("ep = tblink.get_default_ep();")
        out.println()
        out.println("if (ep == null) begin")
        out.inc_ind()
        out.println("$display(\"Error: no default endpoint\");")
        out.println("$finish();")
        out.dec_ind()
        out.println("end")
        out.println()
        
        out.println("iftype = define_type(ep);")
        out.println()
        
        out.println("ifimpl = new(vif);")
        out.println("ifinst = ep.defineInterfaceInst(")
        out.inc_ind()
        out.println("iftype,")
        out.println("inst_name,")
        if is_mirror:
            out.println("1,")
        else:
            out.println("0,")
        out.println("ifimpl);")
        out.dec_ind()
        
        out.dec_ind()
        out.println("endfunction")
        
        out.println()
        out.println("function automatic IParamVal invoke_nb(")
        out.inc_ind()
        out.println("input IInterfaceInst         ifinst,")
        out.println("input IMethodType            method,")
        out.println("input IParamValVec           params);")
        out.dec_ind()
        out.println("endfunction")
        out.println()
        
        out.println("task automatic invoke_b(")
        out.inc_ind()
        out.println("output IParamVal retval,")
        out.println("input IInterfaceInst ifinst,")
        out.println("input IMethodType method,")
        out.println("input IParamValVec params);")
        out.dec_ind()
        out.println("endtask")
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