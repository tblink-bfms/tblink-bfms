'''
Created on Oct 28, 2021

@author: mballance
'''
import os
import jinja2


class TemplateLoader(jinja2.BaseLoader):
    
    def get_source(self, environment, template):
        path = template
        if not os.path.exists(path):
            raise jinja2.TemplateNotFound(template)
        mtime = os.path.getmtime(path)
        f = open(path, "r")
        try:
            source = f.read()
        except:
            print("Error reading file \"" + path + "\"");
        f.close()
        return source, path, lambda: mtime == os.path.getmtime(path) 
    