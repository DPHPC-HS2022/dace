import dace
from dace.config import Config
from dace import dtypes
from dace.codegen.codegen import *
from dace.codegen.compiler import *
import glob, re, json
import os, importlib
import time

def generate_benchmark_code(func, output_path, config, params_dict):
    # Generate SDFG for the function
    sdfg = func.to_sdfg()
         
    # Generate code from the SDFG
    code_objects = generate_code(sdfg,params_dict) # List of code objects  
    generate_program_folder(sdfg, code_objects, output_path, config=config)
    lib_file = configure_and_compile(output_path, program_name="test", output_stream=None)

def execute_benchmark_code(output_path):
    # Compile and Execute
    path = os.getcwd()
    os.chdir(output_path + '/build')
    os.system('gcc -I '+ path +'/../dace/runtime/include/ -o bin ../sample/*.cpp -L . -ltest')
    avg = 0
    N = 10
    for i in range(N):
        st = time.process_time()
        os.system('LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH ./bin')
        et = time.process_time()
        avg += et-st
    print(output_path," Average exec time:",str(avg/N))
    os.chdir(path)

def generate(id):
    config = Config()

    # Read every function name in npbench
    #benchmark_list = glob.glob("./npbench/bench_info/*")
    benchmark_list_file = open("benchmarks.txt","r")

    #for benchmark_info in benchmark_list:
    for benchmark_info in benchmark_list_file:
            # Extract path from json
        
            jsonfile = open(benchmark_info.split(",")[0],"r")
            benchmark_data = json.load(jsonfile)
            jsonfile.close()

            print("BENCHMARK:", benchmark_info)

            # Required json parameters for a benchmark
            rel_path = benchmark_data['benchmark']['relative_path']
            module_name = benchmark_data['benchmark']['module_name']
            func_name = benchmark_data['benchmark']['func_name']
            params_dict = benchmark_data['benchmark']['parameters']['S']

            # Import module
            path_to_import = benchmark_info.split(",")[1]
            rel_path_list = rel_path.split('/')
            for i in range(len(rel_path_list)):
                path_to_import = path_to_import + "." + rel_path_list[i]
                if (i == (len(rel_path_list)-1)):
                    path_to_import = path_to_import + "." + module_name + "_dace"

            print(path_to_import)
            module = importlib.import_module(path_to_import)
        
            # Get function
            func = getattr(module, func_name)
            
            for omp_use_task in [True, False]:
                # Change Config
                Config.set('compiler', 'cpu', 'omp_use_tasks', value = omp_use_task)               
                output_path = "run" + str(id) + "/build-" + rel_path + "-" + func_name + "-useTasks=" + str(omp_use_task)
                
                try:             
                    generate_benchmark_code(func, output_path, config, params_dict)
                    execute_benchmark_code(output_path)
                #except (dace.codegen.exceptions.CompilerConfigurationError, KeyError):
                except Exception as e:
                    print(e)
                    print("### Ignoring benchmark due to Errors !!! \n")

if __name__=="__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--id', type=int, default=1)
    args = vars(argparser.parse_args())
    generate(args["id"])