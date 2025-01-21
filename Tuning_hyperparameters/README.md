DNNGP Auto Hyperparameters Optimization Script

This directory contains the DNNGP auto hyperparameters tuning script, which accomplishes two main functions:
1. It automatically optimizes the hyperparameters of DNNGP and outputs the best results as a JSON file.
2. It automatically tunes hyperparameters for multiple phenotypic traits.

This script has certain requirements for package versions, so it is necessary to recreate the conda environment for DNNGP3. Two YAML files are provided in this directory, corresponding to the runtime environments for Linux and Windows respectively. You can use the command `conda env create -f DNNGP_Linux_OPN.yaml` to create the corresponding environment.

Regarding the use of the script:
You can create a directory that contains a pkl file (genotype file) and multiple corresponding tsv files (each tsv file contains one phenotype), and then specify the directory within this script to the newly created directory to run the script. The generated best parameters json file will also be output in this directory. The file directory structure is as follows:

```
Inputfiles/
│
├── genotype.pkl
├── phenotype1.tsv
├── phenotype2.tsv
├── phenotype3.tsv
├──...
└── phenotypeN.tsv
```
:star2:Tips:
After experiments, it was found that some users may encounter the issue of being unable to use the GPU after installing the environment. After activating the `DNNGP3` environment, you can try the following command to solve the problem:
```
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export PATH=$CONDA_PREFIX/bin:$PATH
```
More information about the script is described in the script file in the form of comments.  
:telephone_receiver:If there are problems with use, please contact us.
