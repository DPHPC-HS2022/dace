#!/bin/bash
git clone https://github.com/spcl/npbench.git
cd npbench/
python -m pip install -r requirements.txt
python -m pip install .
python -m pip install numba

