#!/bin/bash
DIR=npbench
if [ ! -d "$DIR" ]; # Check if we haven't clone npbench yet
then
    git clone https://github.com/spcl/npbench.git
fi
cd npbench/
if ! [ -x "$(command -v pip)" ]; # Check if pip exists 
then 
    python -m pip install -r requirements.txt
    python -m pip install .
    python -m pip install numba
else 
    pip3 install -r requirements.txt
    pip3 install .
    pip3 install numba
fi

