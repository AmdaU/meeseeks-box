#!/bin/sh

cp parameters_example.dat parameters

python3 -m venv .venv
source .venv/bin/activate
pip install poetry
poetry install
