import dace as dc
import numpy as np

N, M = (dc.symbol(s, dtype=dc.int64) for s in ('N', 'M'))

@dc.program
def test_func():
    res = np.zeros((M, ), dtype=np.int64)
    for i in dc.map[0:M]:
        lim = 1
        for k in dc.map[0:i+1]:
            lim *= N
        on_values = 0.0
        for j in dc.map[0:lim]:
            on_values += 1.0
        res[i] = on_values
    return res
