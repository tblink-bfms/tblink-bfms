'''
Created on Oct 27, 2021

@author: mballance
'''
import os

import jinja2
from setuptools.command.build_ext import build_ext
from tblink_rpc_utils.yaml_idl_parser import YamlIDLParser
from distutils.extension import Extension
import shutil
from tblink_bfms.template_loader import TemplateLoader
from tblink_bfms.generators.gen_rgy import GenRgy


class BfmBuildExtCmd(build_ext):
    """
    Implementation of the 'build_ext' command that supports building BFMs
    """
    
    def run(self):
        bfm_extensions = []
        self.gen_i = None
        self.idl = None

        self.debug = False

        if self.debug:        
            print("BfmBuildExtCmd")
            print("  build_lib=%s" % self.build_lib)
            print("  package=%s" % self.package)
       
        i=0
        while i < len(self.extensions):
            if self.extensions[i].name.endswith(".yaml"):
                bfm_extensions.append(self.extensions[i])
                self.extensions.pop(i)
            else:
                i += 1

        if os.path.isdir(self.build_lib):
            # Process BFM extensions
            pkg_dir = None
            for f in os.listdir(self.build_lib):
                if os.path.isdir(os.path.join(self.build_lib, f)):
                    if os.path.isfile(os.path.join(self.build_lib, f, "__init__.py")):
                        pkg_dir = os.path.join(self.build_lib, f)
                        break
                
            if pkg_dir is None:
                raise Exception("Failed to find package in %s" % self.build_lib)
            share_dir = os.path.join(pkg_dir, "share")
        
            if not os.path.isdir(share_dir):
                os.makedirs(share_dir)
        else: # Installing in 'dev' mode
            share_dir = os.getcwd()

        self.env = jinja2.Environment(loader=TemplateLoader())
        
        for ext in bfm_extensions:
            self.build_bfm_ext(ext, share_dir)

        # Build any non-BFM extensions   
        build_ext.run(self)

        
    def build_bfm_ext(self, ext : Extension, share_dir):
        parser = YamlIDLParser()
        self.idl = None
        with open(ext.name, "r") as fp:
            self.idl = parser.parse(fp)

        for src in ext.sources:
            self.process_files(
                src, 
                os.path.join(share_dir, os.path.basename(src)))
            

    def process_files(self, src_dir, dst_dir):
        for src_f in os.listdir(src_dir):
            if os.path.isdir(os.path.join(src_dir, src_f)):
                if src_f not in (".", ".."):
                    self.process_files(
                        os.path.join(src_dir, src_f),
                        os.path.join(dst_dir, src_f))
            elif src_f.endswith(".in"):
                # Template file
                if self.debug:        
                    print("Template file %s" % os.path.join(src_dir, src_f))
                if not os.path.isdir(os.path.join(dst_dir)):
                    os.makedirs(os.path.join(dst_dir))
                self.process_template(
                    os.path.join(src_dir, src_f),
                    dst_dir)
            elif src_dir != dst_dir:
                # Just copy over
                if self.debug:        
                    print("Copying file %s" % os.path.join(src_dir, src_f))
                if not os.path.isdir(os.path.join(dst_dir)):
                    os.makedirs(os.path.join(dst_dir))
                shutil.copy(
                    os.path.join(src_dir, src_f),
                    os.path.join(dst_dir, src_f))
            else:
                if self.debug:        
                    print("src_dir==dst_dir")
                
    def process_template(self, src_file, dst_dir):
        tmpl_e = self.get_template(src_file)
        
        if not hasattr(tmpl_e.module, "tblink_generators"):
            raise Exception("tblink_generators not set")
        
        if not isinstance(tmpl_e.module.tblink_generators, dict):
            raise Exception("tblink_generators is not a dict")
        
        for file,gen in tmpl_e.module.tblink_generators.items():
            if self.debug:        
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
            if self.debug:        
                print("iftype=%s is_mirror=%s" % (iftype, str(is_mirror)))

            iftype_i = self.idl.find_iftype(iftype)

            if iftype_i is None:
                raise Exception("Failed to find interface type %s" % iftype)
            
            return self.gen_i.tblink_gen(iftype_i, is_mirror, kind, **kwargs)
        else:
            return ""
    
        
