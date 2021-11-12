'''
Created on Oct 27, 2021

@author: mballance
'''
from argparse import ArgumentParser
import argparse
from tblink_bfms.cmd_gen import cmd_gen

def get_parser():
    parser : ArgumentParser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'
    
    gen_cmd = subparsers.add_parser("gen",
        help="Generate BFM files from input specs")
    gen_cmd.add_argument("-o", "--outdir", 
        help="Specifies result directory")
    gen_cmd.add_argument("source", nargs='+',
        help="Template source files and root YAML file")
    gen_cmd.set_defaults(func=cmd_gen)
    
    
    return parser

def main():
    parser = get_parser()
    
    args = parser.parse_args()
    
    args.func(args)
    

if __name__ == "__main__":
    main()
