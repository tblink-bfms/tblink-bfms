
BFM components are stored in multiple folders within the project.
For flexibility, the structure of these folders isn't specified.

BFM sources (folders) are specified as the sources for a BFM extension.
The root IDL YAML file is specified as the identifier of the extension,
which allows it to be identified.

BFMs are built in one of two ways depending on how the Python project
is treated.

## Editable Install
Generated BFM files are created alongside the source files. Users should
mark this files as "git ignore" to avoid committing them to source control.

Note: In this configuration, the BFM files are outside the Python 
package. 

## Distributed Wheel
BFM files are copied to the build directory, and generated files added
alongside. 

Note: In this configuration, the BFM files are inside a `share` 
subdirectory of the Python package.

## Pre-Built Install
BFM files (source and generated) have been packed with the Python `wheel`
when it was built. Files are simply installed as any other data file.

# Wheel Build Process
- Build_py is instructed to copy Python files are copied to the build directory
- BuildExt is instructed to build with an output of the build directory (no package)
  - The package directory does exist, so perhaps we can probe?
- Dist is instructed to copy the structure of the build directory to
  produce an output. 
  
Looks like we only need to ensure that the BFM files end up
in the proper sub-directory inside build in order to have 
them included in the built package

