# Setup

Setup npbench benchmark by running 
```
bash setup_benchmark.sh
```
# Run benchmarks 

Run the benchmark (specify the ./run-id/ directory if required, default is ./run1/)
Reads the dace benchmark programs from benchmarks.txt, generates code for openmp tasks and parallel for, compiles and runs the generated C code.
```
python code_generator.py --id 1
```

# Adding benchmarks

benchmarks.txt contains the benchmarks to be run and the path to the benchmark-folder
1. Create a json file containing, parameters of the module name (name of the python file), function name (name of the function within the file), relative path (with respect to benchmark-folder),...
2. Add the path of the json file to benchmarks.txt