#!/bin/bash

if [ ! -f parameters.dat ]; then cp parameters_example.dat parameters.dat; 
  fi

mkdir log
touch log/history.txt

python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
