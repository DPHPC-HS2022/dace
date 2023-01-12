import dace as dc
import numpy as np

@dc.program
def fibonacci(v: dc.int32):
    a=0
    b=1
    while(v-2):
        c=a+b
        a=b
        b=c
        v=v-1