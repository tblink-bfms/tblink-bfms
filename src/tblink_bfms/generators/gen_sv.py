'''
Created on Nov 12, 2021

@author: mballance
'''
from tblink_rpc.gen_utils import GenUtils


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
        pass
    
    def gen_method_t_find(self, out, iftype, is_mirror, **kwargs):
        pass

