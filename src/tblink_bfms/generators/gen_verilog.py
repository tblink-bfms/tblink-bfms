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

        out.inc_ind()
        for m in iftype.methods:
            if not m.is_export and not is_mirror or m.is_export and is_mirror:
                if m.is_blocking:
                    self.gen_method_t_impl_b(out, m, "m_ifinst")
                else:
                    self.gen_method_t_impl_nb(out, m, "m_ifinst")
        out.dec_ind()
        
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
        
    def gen_method_t_impl_b(self, out, m, prefix="m_ifinst", qtype=False, is_auto=False):
        
        if qtype:
            tpref = "tblink_rpc::"
        else:
            tpref = ""
            
        out.println("task %s(" % m.name)
        out.inc_ind()
        out.inc_ind()

        if m.rtype is not None:
            # Return passed as the first parameter
            out.write("%soutput %s rval" % (out.ind, self._type2str(m.rtype)))
            
        for i,p in enumerate(m.params):
            if i > 0 or m.rtype is not None:
                out.write(",\n%s" % out.ind)
            out.write("%sinput " % out.ind)
            self.gen_sv_typename(out, p[1])
            out.write(" %s" % p[0])
            
        if len(m.params) > 0:
            out.write(");\n")
        else:
            out.write("%s);\n" % out.ind)

        out.dec_ind()
        out.dec_ind()
        out.println("begin")
        out.inc_ind()
        
        # TODO: internals
        out.println("%sIParamValVec params = m_ifinst.mkValVec();" % tpref)
        out.println("%sIParamVal retval;" % tpref)
        
        for i,p in enumerate(m.params):
            out.println("params.push_back(%s);" % self._mktblink_val(p[1], p[0], "m_ifinst"))

        out.println("$display(\"m_ifinst=%%p\", %s);" % prefix)

        out.write(out.ind)
        if m.rtype is not None:
            out.write("retval = ")
        else:
#            out.write("void'(")
#            out.write("rval = ")
            pass
            
        out.write("%s.invoke_b(\n" % prefix)
        out.inc_ind()
        out.println("retval,")
        out.println("m_%s," % m.name)
        if m.rtype is not None:
            out.println("params);")
        else:
#            out.println("params));")
            out.println("params);")
        out.dec_ind()
        out.dec_ind()
        out.println("end")
        out.println("endtask")

    def gen_method_t_impl_nb(self, out, m, prefix="m_ifinst", qtype=False, is_auto=False):
        
        if qtype:
            tpref = "tblink_rpc::"
        else:
            tpref = ""
        if is_auto:
            auto = "automatic "
        else:
            auto = ""
            
        if m.rtype is None:
            # Older Verilog simulators don't like void functions. Use tasks instead
            out.println("task %s(" % m.name)
        else:
            out.println("function %s %s(" % (self._type2str(m.rtype), m.name))

        out.inc_ind()
        out.inc_ind()
            
        for i,p in enumerate(m.params):
            if i > 0 or m.rtype is not None:
                out.write(",\n%s" % out.ind)
            out.write("%sinput " % out.ind)
            self.gen_sv_typename(out, p[1])
            out.write(" %s" % p[0])
            
            
        if len(m.params) > 0:
            out.write(");\n")
        else:
            out.write("%s);\n" % out.ind)
        out.dec_ind()

        out.println("reg[63:0] params;")
        out.println("reg[63:0] retval = 0;")
        if m.rtype is not None:
            out.println("%s rval;" % self._type2str(m.rtype))
        out.dec_ind()
        out.println("begin")
        out.inc_ind()
        
        out.println("params = $tblink_rpc_IInterfaceInst_mkValVec(%s);" % prefix)
        
        # if m.rtype is not None:
        #     # Return passed as the first parameter
        #     out.println("%s retval;" % self._type2tblinkstr(m.rtype, qtype))
        #     out.println("%s rval;" % self._type2str(m.rtype))
        # else:
        #     out.println("tblink_rpc::IParamVal rval;")
        
        for i,p in enumerate(m.params):
            out.println("$tblink_rpc_IParamValVec_push_back(params, %s);" % self._mktblink_val(p[1], p[0], prefix))

        out.println("$display(\"m_ifinst=%%p\", %s);" % prefix)

        out.write(out.ind)
        if m.rtype is not None:
            out.write("retval = ")
        else:
#            out.write("void'(")
            out.write("rval = ")
            
        out.write("$tblink_rpc_IInterfaceInst_invoke_nb(\n" % prefix)
        out.inc_ind()
        out.println("m_%s," % m.name)
        if m.rtype is not None:
            out.println("params);")
        else:
#            out.println("params));")
            out.println("params);")
        out.dec_ind()
                
        # TODO: internals
        
        if m.rtype is not None:
            out.println("return rval;")
        out.dec_ind()

        out.println("end")        
        if m.rtype is None:
            out.println("endtask")
        else:
            out.println("endfunction")

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
    