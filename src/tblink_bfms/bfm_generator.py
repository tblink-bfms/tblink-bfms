'''
Created on Oct 27, 2021

@author: mballance
'''
import os
import shutil

import jinja2

from tblink_bfms.generators.gen_rgy import GenRgy
from tblink_bfms.template_loader import TemplateLoader
from tblink_rpc.yaml_idl_parser import YamlIDLParser


class BfmGenerator(object):
    
    def __init__(self, outdir):
        self.outdir = outdir
        self.env = jinja2.Environment(loader=TemplateLoader())
        self.gen_i = None
        pass
    
    def generate(self, idl_file, sources):
        
        parser = YamlIDLParser()
        self.idl = None
        with open(idl_file, "r") as fp:
            self.idl = parser.parse(fp)

        for src in sources:
            self.process_files(
                src, 
                os.path.join(self.outdir, os.path.basename(src)))
        pass
    
    def process_files(self, src_dir, dst_dir):
        for src_f in os.listdir(src_dir):
            if os.path.isdir(os.path.join(src_dir, src_f)):
                if src_f not in (".", ".."):
                    self.process_files(
                        os.path.join(src_dir, src_f),
                        os.path.join(dst_dir, src_f))
            elif src_f.endswith(".in"):
                # Template file
                print("Template file %s" % os.path.join(src_dir, src_f))
                if not os.path.isdir(os.path.join(dst_dir)):
                    os.makedirs(os.path.join(dst_dir))
                self.process_template(
                    os.path.join(src_dir, src_f),
                    dst_dir)
            else:
                # Just copy over
                print("Copying file %s" % os.path.join(src_dir, src_f))
                if not os.path.isdir(os.path.join(dst_dir)):
                    os.makedirs(os.path.join(dst_dir))
                shutil.copy(
                    os.path.join(src_dir, src_f),
                    os.path.join(dst_dir, src_f))
                
    def process_template(self, src_file, dst_dir):
        tmpl_e = self.get_template(src_file)
        
        if not hasattr(tmpl_e.module, "tblink_generators"):
            raise Exception("tblink_generators not set")
        
        if not isinstance(tmpl_e.module.tblink_generators, dict):
            raise Exception("tblink_generators is not a dict")
        
        for file,gen in tmpl_e.module.tblink_generators.items():
            print("Generate for %s:%s" % (file, gen))
            dst_file = os.path.join(dst_dir, file)
            gen_t = GenRgy.inst().find_gen(gen)
            
            if gen_t is None:
                raise Exception("Generator type %s does not exist" % gen)
            
            self.gen_i = gen_t()
       
            content = tmpl_e.render()
#            content = ""
                
            with open(dst_file, "w") as fp:
                fp.write(content)
                
            self.gen_i = None
            
    def get_template(self, path):
        tmpl_e = self.env.get_template(path)
        tmpl_e.globals["tblink_gen"] = self.gen_tblink_gen
        return tmpl_e
    
    def gen_tblink_gen(self, iftype, is_mirror, kind=None, **kwargs):
        if self.gen_i is not None:
            print("iftype=%s is_mirror=%s" % (iftype, str(is_mirror)))

            iftype_i = self.idl.find_iftype(iftype)

            if iftype_i is None:
                raise Exception("Failed to find interface type %s" % iftype)
            
            return self.gen_i.tblink_gen(iftype_i, is_mirror, kind, **kwargs)
        else:
            return ""    
        