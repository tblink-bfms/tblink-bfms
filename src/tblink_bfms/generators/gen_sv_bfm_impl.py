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
        
        out.println("tblink_rpc::IInterfaceInst m_ifinst;")
        
        # Generate handles for import methods
        for m in iftype.methods:
            if not m.is_export and not is_mirror or m.is_export and is_mirror:
                out.println("tblink_rpc::IMethodType m_%s;" % m.name)
        out.println()
        
        # Generate import methods
        for m in iftype.methods:
            if not m.is_export and not is_mirror or m.is_export and is_mirror:
                if m.is_blocking:
                    GenSv().gen_method_t_impl_b(out, m, "m_ifinst", qtype=True, is_auto=True)
                else:
                    GenSv().gen_method_t_impl_nb(out, m, "m_ifinst", qtype=True, is_auto=True)
                    
        out.println()

        # Generate type-definition method
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
        out.println("IInterfaceType iftype;")
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
        out.println("SVInterfaceImplVif #(vif_t) ifimpl;")
        out.println()
        out.println("$display(\"init: %s\", inst_name);")        
        out.println("ep = tblink.get_default_ep();")
        out.println("$display(\"init: post-get-default\");")
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
        out.println("$display(\"init: define-interface-inst\");")
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
        out.inc_ind()
        out.println("input IInterfaceInst         ifinst,")
        out.println("input IMethodType            method,")
        out.println("input IParamValVec           params);")
        out.dec_ind()
        out.println()
        out.println("IParamVal retval;")
        out.println()
        out.println("case (method.id())")
        out.inc_ind();
        for i,m in enumerate(iftype.methods):
            if not m.is_blocking and (is_mirror and not m.is_export or not is_mirror and m.is_export):
                GenSv().gen_invoke_nb_case(out, i, m, "")
        out.println("default: begin")
        out.inc_ind()
        out.println("$display(\"TbLink Fatal: Invalid method-id %0d to instance %m\", method.id());")
        out.dec_ind()
        out.println("end")
        
        out.dec_ind();
        out.println("endcase")
       

        out.println("return retval;")
        out.dec_ind()
        out.println("endfunction")
        out.println()
        
        out.println("task automatic invoke_b(")
        out.inc_ind()
        out.inc_ind()
        out.println("output IParamVal retval,")
        out.println("input IInterfaceInst ifinst,")
        out.println("input IMethodType method,")
        out.println("input IParamValVec params);")
        out.dec_ind()
        
        out.println("case (method.id())")
        out.inc_ind();
        for i,m in enumerate(iftype.methods):
            if m.is_blocking and (is_mirror and not m.is_export or not is_mirror and m.is_export):
                GenSv().gen_invoke_b_case(out, i, m, "")
                pass
        out.println("default: begin")
        out.inc_ind()
        out.println("$display(\"TbLink Fatal: Invalid method-id %0d to instance %m\", method.id());")
        out.dec_ind()
        out.println("end")
        
        out.dec_ind();
        out.println("endcase")
        
        out.dec_ind()
        out.println("endtask")
        out.println()
        
        out.println("endinterface")
        out.println()

        out.println("%s_core u_core();" % g_util.to_id(iftype.name))
        out.println()
        
        # Generate call-out methods for the BFM implementation to call
        for m in iftype.methods:
            pass
        
        out.println()
        
        out.println("initial begin")
        out.inc_ind()
        out.println("$display(\"rv_bfm: %m\");")
        out.println("m_inst_name = $sformatf(\"%m\");")
        out.println("u_core.init(")
        out.inc_ind()
        out.println("m_inst_name,")
        out.println("u_core);")
        out.dec_ind()
        out.println()
        out.println("m_ifinst = u_core.ifinst;")
        out.println()
        
        # Find the method handles
        out.println("// Lookup method handles")
        for m in iftype.methods:
            if m.is_export == is_mirror:
                out.println("m_%s = u_core.iftype.findMethod(\"%s\");" % (
                    m.name, m.name))
        
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
                GenSv().gen_invoke_b_case(out, i, m, "")
#                out.println("%d: begin // %s" % (i, m.name))
#                out.inc_ind()
#                out.dec_ind()
#                out.println("end")
#                out.println()
        out.println("default: begin")
        out.inc_ind()
        out.println("$display(\"TbLink Error: %%m - unknown method id %%0d\", id);")
        out.println("$stop;")
        out.dec_ind()
        out.println("end")
        out.println("endcase")

        out.println()
        out.println("return retval_h;")
        out.dec_ind()
        out.println("endfunction")
        out.println("export \"DPI-C\" function %s_core_invoke_nb;" % g_util.to_id(iftype.name))
        out.println()

        out.println("function automatic void init();")
        out.inc_ind()
        out.println("tblink_rpc::TbLink tblink = tblink_rpc::tblink();");
        out.println("tblink_rpc::IEndpoint ep;")
        out.println("tblink_rpc::IInterfaceType iftype;")
        out.println("tblink_rpc::DpiInterfaceImpl ifimpl;")
        out.println("int ret;")
        out.println()
        out.println("$display(\"init for %0s\", m_inst_name);")
#        out.println("tblink = tblink_rpc::TbLink::inst();")
        out.println("ep = tblink.get_default_ep();")
        out.println()
        out.println("if (ep == null) begin")
        out.inc_ind()
        out.println("$display(\"TbLink Error: no default endpoint\");")
        out.println("$finish();")
        out.dec_ind()
        out.println("end")
        
        
        out.println()
        out.println("ret = tblink_rpc::tblink_rpc_register_dpi_bfm(")
        out.inc_ind()
        out.inc_ind()
        out.println("m_inst_name,")
        out.println("string'(\"%s_core_invoke_nb\")," % g_util.to_id(iftype.name))
        out.println("string'(\"%s_core_invoke_nb\"));" % g_util.to_id(iftype.name))
#        out.println("string'(\"def\"));")
        out.dec_ind()
        out.dec_ind()
        
        out.println("if (ret == -1) begin")
        out.inc_ind()
        out.println("$display(\"TbLink Error: failed to register DPI BFM %0s\", m_inst_name);")
        out.println("$finish();")
        out.dec_ind()
        out.println("end")
        
        out.println("iftype = define_type(ep);")
        
        out.println()
        out.println("ifimpl = new(m_inst_name);")
        
        out.println()
        out.println("m_ifinst = ep.defineInterfaceInst(")
        out.inc_ind()
        out.inc_ind()
        out.println("iftype,")
        out.println("m_inst_name,")
        if is_mirror:
            out.println("1,")
        else:
            out.println("0,")
        out.println("ifimpl);")
        out.dec_ind()
        out.dec_ind()
        
        out.dec_ind()
        out.println("endfunction")
       
        out.println("initial begin")
        out.inc_ind()
        out.println("m_inst_name = $sformatf(\"%m\");")
        out.println("init();")
        out.println("tblink_rpc::tblink_rpc_start();")
        out.dec_ind()
        out.println("end")
