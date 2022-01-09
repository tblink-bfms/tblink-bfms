'''
Created on Oct 29, 2021

@author: mballance
'''
from _io import StringIO

from tblink_bfms.generators.gen_base import GenBase
from tblink_rpc_utils.gen_utils import GenUtils
from tblink_rpc_utils.output import Output
from tblink_rpc_utils.type_spec import TypeSpec, TypeKind


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

        out.inc_ind()
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
        
        out.println("// Create interface instance")
        out.println("m_ifinst = $tblink_rpc_IEndpoint_defineInterfaceInst(")
        out.inc_ind()
        out.inc_ind()
        out.println("m_ep,")
        out.println("m_iftype,")
        out.println("\"\",")
        out.println("0,")
        out.println("m_ev);")
        out.dec_ind()
        out.dec_ind()
        
        out.println()
        out.println("// Lookup method handles")
        self.gen_method_lookup(out, iftype, is_mirror)
        out.println()
        out.println("// Event-processing loop")
        out.println("while (1) begin : invoke_loop")
        out.inc_ind()
        out.println("reg[31:0] ret;")
        out.println("reg[63:0] method;")
        out.println("reg[63:0] call_id;")
        out.println("reg[63:0] params;")
        out.println()
        out.println("ret = $tblink_rpc_InterfaceInstWrapper_nextInvokeReq(")
        out.inc_ind()
        out.inc_ind()
        out.println("m_ifinst,")
        out.println("method,")
        out.println("call_id,")
        out.println("params);")
        out.dec_ind()
        out.dec_ind()
        out.println()
        out.println("$display(\"ret=%0d\", ret);")
        out.println()
        out.println("if (ret == 1) begin : invoke_avail")
        out.inc_ind()
        out.println("reg[31:0] id;")
        out.println()
        out.println("id = $tblink_rpc_IMethodType_id(method);")
        out.println()
        out.println('$display("id=%0d", id);')
        out.println()
        
        out.println("case (id)")
        for i,m in enumerate(iftype.methods):
            if is_mirror and not m.is_export or not is_mirror and m.is_export:
                if m.is_blocking:
                    self.gen_invoke_b_case(out, i, m)
                else:
                    self.gen_invoke_nb_case(out, i, m)
        out.println("default: begin")
        out.inc_ind()
        out.println("$display(\"TbLink Error: %m unknown call-id %0d\", m_id);")
        out.println("$finish;")
        out.println("@(m_ev);")
        out.dec_ind()
        out.println("end")
        out.println("endcase")
        out.dec_ind()
        out.println("end else begin // No message available")
        out.inc_ind()
        out.println("@(m_ev);")
        out.dec_ind()
        out.println("end")
        out.dec_ind()
        out.println("end")
        out.dec_ind()
        out.println("end")

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
        out.println("reg[31:0]    m_id     = 0;")
        out.println("reg[63:0]    m_ep     = 0;")
        out.println("reg[63:0]    m_iftype = 0;")
        out.println("reg[63:0]    m_ifinst = 0;")
        for m in iftype.methods:
            if not m.is_export and not is_mirror or m.is_export and is_mirror:
                out.println("reg[63:0]    m_%s;" % m.name)
        out.dec_ind()
        pass
    
    def gen_method_lookup(self, out, iftype, is_mirror):
        for m in iftype.methods:
            if not m.is_export and not is_mirror or m.is_export and is_mirror:
                out.println("m_%s = $tblink_rpc_IInterfaceType_findMethod(m_iftype, \"%s\");" % (
                    m.name, m.name))

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

        if len(m.params) == 0 and m.rtype is None:
            out.println("task %s;" % m.name)
        else:
            out.println("task %s(" % m.name)
            out.inc_ind()
            out.inc_ind()

            if m.rtype is not None:
                # Return passed as the first parameter
                out.write("%soutput %s rval" % (out.ind, self._type2str(m.rtype)))
            
            for i,p in enumerate(m.params):
                if i > 0 or m.rtype is not None:
                    out.write(",\n%s" % out.ind)
                out.write("%sinput %s %s" % (
                    out.ind,
                    out._type2str(p[1]),
                    p[0]))

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
            out.println("pvalue = %s;" % self._mktblink_val(p[1], p[0], "m_ifinst"))
            out.println("params.push_back(pvalue);")

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
            out.write("%stask %s" % (out.ind, m.name))
        else:
            out.write("%sfunction %s %s" % (out.ind, self._type2str(m.rtype), m.name))


        out.inc_ind()
        if len(m.params) == 0:
            out.write(";\n")
        else:                        
            out.inc_ind()
            out.write("(\n")
            for i,p in enumerate(m.params):
                if i > 0 or m.rtype is not None:
                    out.write(",\n%s" % out.ind)
                out.write("%sinput %s %s" % (
                    out.ind,
                    self._type2str(p[1]),
                    p[0]))
            
            if len(m.params) > 0:
                out.write(");\n")
            else:
                out.write("%s);\n" % out.ind)
            out.dec_ind()

        out.println("reg[63:0] pvalue;")
        out.println("reg[63:0] params;")
        out.println("reg[63:0] retval;")
        out.println("reg[63:0] rval;")
        out.dec_ind()
        out.println("begin")
        out.inc_ind()
        
        out.println("retval = 0;")
        out.println("params = $tblink_rpc_InterfaceInstWrapper_mkValVec(%s);" % prefix)
        
        # if m.rtype is not None:
        #     # Return passed as the first parameter
        #     out.println("%s retval;" % self._type2tblinkstr(m.rtype, qtype))
        #     out.println("%s rval;" % self._type2str(m.rtype))
        # else:
        #     out.println("tblink_rpc::IParamVal rval;")
        
        for i,p in enumerate(m.params):
            out.println("pvalue = %s;" % self._mktblink_val(p[1], p[0], "m_ifinst"))
            out.println("$tblink_rpc_IParamValVec_push_back(params, pvalue);")

        out.println("$display(\"m_ifinst=%%p\", %s);" % prefix)

        out.write(out.ind)
        if m.rtype is not None:
            out.write("retval = ")
        else:
#            out.write("void'(")
            out.write("rval = ")
            
        out.write("$tblink_rpc_InterfaceInstWrapper_invoke_nb(\n")
        out.inc_ind()
        out.println("%s," % prefix)
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
            
    def gen_invoke_b_case(self, out, i, m):
        out.println("%d : begin : _invoke_%s" % (i, m.name))
        out.inc_ind()
        out.println("reg[63:0]    retval_h;")
        out.println("reg[63:0]    param_h;")
        
        if m.rtype is not None:
            out.println("%s retval;" % self._type2str(m.rtype))

        # Declare variables for parameters        
        for p in m.params:
            out.println("%s _param_%s;" % (self._type2str(p[1]), p[0]))
        
        out.println("retval_h = 0;")

        # Fetch parameter values        
        for i,p in enumerate(m.params):
            out.println("param_h = $tblink_rpc_IParamValVec_at(params, %d);" % i);
            if p[1].kind == TypeKind.Int:
                if p[1].is_signed:
                    out.println("_param_%s = $tblink_rpc_IParamValInt_val_s(param_h);" % p[0])
                else:
                    out.println("_param_%s = $tblink_rpc_IParamValInt_val_u(param_h);" % p[0])
            else:
                raise Exception("Unsupported parameter %s in method %s" % (
                    str(p[1].kind), p[0]))
                
        out.println()
       

        if len(m.params) == 0 and m.rtype is None:
            out.println("%s;" % m.name)
        else:        
            out.println("%s(" % m.name)
            out.inc_ind()
            out.inc_ind()
            for i,p in enumerate(m.params):
                if i+1 < len(m.params):
                    out.println("_param_%s," % p[0])
                else:
                    out.println("_param_%s" % p[0])
            out.dec_ind()
            out.println(");")
            out.dec_ind()

        out.println()
        out.println("$tblink_rpc_InterfaceInstWrapper_invoke_rsp(")
        out.inc_ind()
        out.inc_ind()
        out.println("m_ifinst,")
        out.println("call_id,")
        out.println("retval_h")
        out.dec_ind()
        out.println(");")
        out.dec_ind()

        out.dec_ind()
        out.println("end")
        pass
            
    def gen_invoke_nb_case(self, out, i, m):
        out.println("%d : begin : %s" % (i, m.name))
        out.inc_ind()
        out.dec_ind()
        out.println("end")
        pass
    
    def _mktblink_val(self, type_s : TypeSpec, name, ifinst):
        ret = ""
        
        if type_s.kind == TypeKind.Int:
            if type_s.is_signed:
                ret += "$tblink_rpc_InterfaceInstWrapper_mkValIntS(%s, %s, %d)" % (ifinst, name, type_s.width)
            else:
                ret += "$tblink_rpc_InterfaceInstWrapper_mkValIntU(%s, %s, %d)" % (ifinst, name, type_s.width)
        elif type_s.kind == TypeKind.Bool:
            ret += "$tblink_rpc_InterfaceInstWrapper_mkValBool(%s, %s)" % (ifinst, name)
        elif type_s.kind == TypeKind.Str:
            ret += "$tblink_rpc_InterfaceInstWrapper_mkValStr(%s, %s)" % (ifinst, name)
        else:
            raise Exception("Unhandled type: %s" % str(type_s))
        
        return ret    
    
    _int_type_u_m = {
        8: 'reg[7:0]',
        16: 'reg[15:0]',
        32: 'reg[31:0]',
        64: 'reg[63:0]'}
    
    _int_type_s_m = {
        8: 'reg signed[7:0]',
        16: 'reg signed[15:0]',
        32: 'reg signed[31:0]',
        64: 'reg signed[63:0]'}
    
    def _type2str(self, type_s : TypeSpec):
        if type_s.kind == TypeKind.Int:
            if not type_s.is_signed:
                ret = GenVerilog._int_type_s_m[type_s.width]
            else:
                ret = GenVerilog._int_type_u_m[type_s.width]
        elif type_s.kind == TypeKind.Bool:
            ret = "reg"
        elif type_s.kind == TypeKind.Str:
            ret = "string"
        else:
            raise Exception("Unsupported typespec %s" % str(type_s.kind))
            pass
        
        return ret

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
    