'''
Created on Oct 27, 2021

@author: mballance
'''
import os

import jinja2


class BfmGenerator(jinja2.BaseLoader):
    
    def __init__(self):
        pass
    
    def generate(self, bfm_template, outdir=None):
        self.bfm_template = bfm_template
        
        env = jinja2.Environment(loader=self)
        tmpl_e = env.get_template(self.bfm_template)
        
        tmpl_e.globals["tblink_bfm_driver"] = self.tblink_bfm_driver
        tmpl_e.globals["tblink_generator"] = "tblink.bfm.sv"
        
        print("generators: %s" % str(tmpl_e.module.tblink_generators))
        
        print("Render: %s" % tmpl_e.render())
        
        pass
    
    def tblink_bfm_driver(self, iftype, is_mirror):
        print("tblink_bfm_driver: %s %s" % (iftype, str(is_mirror)))
        return "content"
    
    def get_source(self, env, template):
        source = ""
        path = self.bfm_template
        mtime = os.path.getmtime(path)
        with open(path, "r") as fp:
            source = fp.read()

        return source, path, lambda: mtime == os.path.getmtime(path)
        