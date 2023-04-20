import os
from json import load

script_dir = os.path.dirname(os.path.realpath(__file__))

presets = {}
with open(f"{script_dir}/ressources/presets.json") as read:
    presets = load(read)

with open(f"{script_dir}/parameters.dat") as params_file:
    for parameter_line in params_file.readlines():
        parameter_line = parameter_line.strip(" \n\t")
        name, value = parameter_line.split("=")
        globals()[name] = value
