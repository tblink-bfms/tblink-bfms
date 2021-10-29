
BFM packages are designed to support multiple ecosystems. This means 
that, for example, we cannot entirely structure the package according
to Python structure.

# Python Packages
Python is used as a vehicle for delivering BFMs for use with Python,
SystemVerilog, and C++ testbench environments.

Python-based packages must be usable in both source and 
binary (built) form. 

Some portions of the BFM are generated during package build. 
- Could be during from-source install
- Could be during wheel build

Need to 'hook' the build and install process
- Build / bdist_wheel must copy BFM source into package, build BFMs
- Install (source) must build BFMs


