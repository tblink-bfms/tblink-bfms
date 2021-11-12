'''
Created on Nov 12, 2021

@author: mballance
'''
import os
from tblink_bfms.bfm_generator import BfmGenerator

def cmd_gen(args):
    
    idl_file = None
    source = []
    
    for p in args.source:
        print("p=%s" % str(p))
        if os.path.isdir(p):
            source.append(p)
        elif os.path.isfile(p):
            if os.path.splitext(p)[1] == '.yaml':
                idl_file = p
            else:
                source.append(p)
        else:
            raise Exception("unknown source")
        
    if idl_file is None:
        raise Exception("No .yaml file specified")
    
    if args.outdir is None:
        args.outdir = "build"
        
    gen = BfmGenerator(args.outdir)
    
    gen.generate(idl_file, source)
            
    pass
