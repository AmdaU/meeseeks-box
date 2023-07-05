#!/bin/bash

cp parameters_example.dat parameters.dat

mkdir log
touch log/history.txt

python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
