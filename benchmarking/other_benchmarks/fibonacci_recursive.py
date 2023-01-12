import dace as dc
import numpy as np

@dc.program
def fibonacci(v: dc.int32):
    if v == 0:
        return 0
    if v == 1:
        return 1
    return fibonacci(v - 1) + fibonacci(v - 2)
