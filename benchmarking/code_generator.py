import dace
from dace.codegen.codegen import *
from dace.codegen.compiler import *
import glob, re, json
import os, importlib

def generate(id):
    # Read every function name in npbench
    benchmark_list = glob.glob("./npbench/bench_info/*")
    for benchmark_info in benchmark_list:

            # Extract path from json
        
            jsonfile = open(benchmark_info,"r")
            benchmark_data = json.load(jsonfile)
            jsonfile.close()

            print("BENCHMARK:", benchmark_info)
            #print(benchmark_data,"\n\n")

            rel_path = benchmark_data['benchmark']['relative_path']
            func_name = benchmark_data['benchmark']['func_name']

            # Import module
            path_to_import = "benchmarking.npbench.npbench.benchmarks"
            rel_path_list = rel_path.split('/')
            for i in range(len(rel_path_list)):
                path_to_import = path_to_import + "." + rel_path_list[i]
                if (i == (len(rel_path_list)-1)):
                    path_to_import = path_to_import + "." + benchmark_data['benchmark']['module_name'] + "_dace"

            print(path_to_import)
            module = importlib.import_module(path_to_import)

            # Get function
            func = getattr(module, func_name)
        
            # Generate SDFG for the function
            sdfg = func.to_sdfg()
         
            # Generate code from the SDFG
            code_objects = generate_code(sdfg) # List of code objects
            output_path = "run" + str(id) + "/build-" + rel_path + "-" + func_name
            generate_program_folder(sdfg, code_objects, output_path, config=None)
            try:
                lib_file = configure_and_compile(output_path, program_name="test", output_stream=None)
            except dace.codegen.exceptions.CompilerConfigurationError:
                print("### Ignoring benchmark due to CompilerConfigurationError !!!")
                continue

            # Compile and Execute
            path = os.getcwd()
            os.chdir('run'+str(id)+'/build-'+rel_path + '-' + func_name + '/build')
            os.system('gcc -I '+ path +'/../dace/runtime/include/ -o bin ../sample/*.cpp -L . -ltest')
            os.system('LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH ./bin')
            os.chdir(path)


if __name__=="__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--id', type=int, default=1)
    args = vars(argparser.parse_args())
    generate(args["id"])