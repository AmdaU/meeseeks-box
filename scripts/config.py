import os
from json import load

script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

presets = {}
with open(f"{script_dir}/ressources/presets.json") as read:
    presets = load(read)

with open(f"{script_dir}/parameters.dat") as params_file:
    parameter_lines = params_file.readlines()
    lines = [line.split("#")[0].strip() for line in parameter_lines if not line.startswith("#")]
    for line in lines:
        name, value = line.split("=")
        globals()[name] = eval(value)
