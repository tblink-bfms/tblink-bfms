'''
Created on Oct 29, 2021

@author: mballance
'''

class GenBase(object):

    def __init__(self):
        pass
    
    def tblink_gen(self, iftype, is_mirror, kind=None, **kwargs):
        raise Exception("Generator class %s does not implement tblink_gen" % (
            str(type(self))))
        
        