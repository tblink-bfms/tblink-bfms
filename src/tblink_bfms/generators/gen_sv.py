'''
Created on Nov 12, 2021

@author: mballance
'''
from tblink_rpc.gen_utils import GenUtils
from tblink_rpc.type_spec import TypeSpec, TypeKind


class GenSv(object):
    
    def __init__(self, is_automatic=False):
        self.is_automatic = is_automatic
    
    def gen_define_type(self, out, iftype, is_mirror, **kwargs):
        g_util = GenUtils(cpp_ptr=False)
        if self.is_automatic:
            out.println("function automatic tblink_rpc::IInterfaceType define_type(tblink_rpc::IEndpoint ep);")
        else:
            out.println("static function tblink_rpc::IInterfaceType define_type(tblink_rpc::IEndpoint ep);")
            
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
        
    def gen_method_t_decl(self, out, iftype, is_mirror, **kwargs):
        """Generates field declarations for method types"""
        for m in iftype.methods:
            out.println("IMethodType m_%s;" % m.name)
    
    def gen_method_t_find(self, out, iftype, is_mirror, **kwargs):
        """Finds method-type handles"""
        out.println("begin")
        out.inc_ind()
        out.println("IInterfaceType iftype = ifinst.iftype();")
        for m in iftype.methods:
            out.println("m_%s = iftype.findMethod(\"%s\");" % (m.name, m.name))
        out.dec_ind()
        out.println("end")
    
    def gen_method_t_impl(self, out, iftype, is_mirror, **kwargs):
        """Generates method implementations"""
        for m in iftype.methods:
            if m.is_blocking:
                out.println("task %s(" % m.name)
                if m.rtype is not None:
                    # TODO: first parameter is return type
                    pass
            else:
                out.write("%sfunction " % out.ind)
                if m.rtype is None:
                    out.write("void")
                else:
                    # TODO: non-void function
                    pass
                out.write(" %s(\n" % m.name)
                
            # Regular user parameters
            out.inc_ind()
            out.inc_ind()
            for i,p in enumerate(m.params):
                if i > 0:
                    out.write(",\n%s" % out.ind)
                out.write("%sinput " % out.ind)
                self.gen_sv_typename(out, p[1])
                out.write(" %s" % p[0])
                pass
            if len(m.params) > 0:
                out.write(");\n")
            else:
                out.write("%s);\n" % out.ind)
                
            out.dec_ind()
        
            # Now, add in handling for different cases
        
            out.dec_ind()
        
            if m.is_blocking:
                out.println("endtask")
            else:
                out.println("endfunction")
                
            out.println()
        
        pass
    
    _int_type_m = {
        8: 'byte',
        16: 'shortint',
        32: 'int',
        64: 'longint'}
    
    def gen_sv_typename(self, out, type_s : TypeSpec):
        if type_s.kind == TypeKind.Int:
            out.write("%s" % GenSv._int_type_m[type_s.width])
            if not type_s.is_signed:
                out.write(" unsigned")
        elif type_s.kind == TypeKind.Bool:
            out.write("bit")
        elif type_s.kind == TypeKind.Str:
            out.write("string")
        else:
            raise Exception("Unsupported typespec %s" % str(type_s.kind))
            pass
        
    def _type2str(self, type_s : TypeSpec):
        if type_s.kind == TypeKind.Int:
            ret = GenSv._int_type_m[type_s.width]
            if not type_s.is_signed:
                ret += " unsigned"
        elif type_s.kind == TypeKind.Bool:
            ret = "bit"
        elif type_s.kind == TypeKind.Str:
            ret = "string"
        else:
            raise Exception("Unsupported typespec %s" % str(type_s.kind))
            pass
        
        return ret
    
    def _type2tblinkstr(self, type_s : TypeSpec):
        if type_s.kind == TypeKind.Int:
            ret = "IParamValInt"
        elif type_s.kind == TypeKind.Bool:
            ret = "IParamValBool"
        elif type_s.kind == TypeKind.Str:
            ret = "IParamValStr"
        else:
            raise Exception("Unsupported typespec %s" % str(type_s.kind))
            pass
        
        return ret
    

    def gen_invoke_nb(self, out, iftype, is_mirror, **kwargs):
        out.println("virtual function IParamVal invoke_nb(")
        out.inc_ind()
        out.inc_ind()
        out.println("input IInterfaceInst ifinst,")
        out.println("input IMethodType method,")
        out.println("input IParamValVec params);")
        out.dec_ind()
        
        out.println("IParamVal retval;")
        out.println()
        out.println("case (method.id())")
        out.inc_ind()
        
        for i,m in enumerate(iftype.methods):
            out.println("%d: begin // %s" % (i, m.name))
            out.inc_ind()
            if m.rtype is not None:
                out.println("%s rval;" % self._type2str(m.rtype))

            for p in m.params:
                out.println("%s %s;" % (self._type2str(p[1]), p[0]))
                out.println("%s %s_p;" % (self._type2tblinkstr(p[1]), p[0]))
            for i,p in enumerate(m.params):
                out.println("$cast(%s_p, params.at(%d));" % (p[0], i))
                if p[1].kind == TypeKind.Int:
                    if p[1].is_signed:
                        out.println("%s = %s_p.val_s();" % (p[0], p[0]))
                    else:
                        out.println("%s = %s_p.val_u();" % (p[0], p[0]))
                else:
                    out.println("%s = %s_p.val();" % (p[0], p[0]))

            out.write("%s" % out.ind)                    
            if m.rtype is not None:
                out.write("rval = ")
            out.write("m_impl.%s(\n" % m.name)
            out.inc_ind()
            out.write("%s" % out.ind)
            for i,p in enumerate(m.params):
                if i > 0:
                    out.write(",\n%s" % out.ind)
                out.write("%s" % p[0])
                
            if len(m.params) > 0:
                out.write(");\n")
            else:
                out.println(");")
                
            out.dec_ind()
                
            out.dec_ind()
            out.println("end")

        out.dec_ind()
        out.println("endcase")
        out.println()
        out.println("return retval;")
        out.dec_ind()
        out.println("endfunction")        
        pass
    
    def gen_invoke_b(self, out, iftype, is_mirror, **kwargs):
        out.println("virtual task invoke_b(")
        out.inc_ind()
        out.inc_ind()
        out.println("output IParamVal retval,")
        out.println("input IInterfaceInst ifinst,")
        out.println("input IMethodType method,")
        out.println("input IParamValVec params);")
        out.dec_ind()
        
        out.println("retval = null;")
        out.println()
        out.println("case (method.id())")
        out.inc_ind()
        for i,m in enumerate(iftype.methods):
            out.println("%d: begin // %s" % (i, m.name))
            out.inc_ind()
            out.dec_ind()
            out.println("end")

        out.dec_ind()
        out.println("endcase")
        out.println()
        out.dec_ind()
        out.println("endtask")           
        pass




    
