import subprocess
from config import *


def execute_code(language, code, std_out=False):
    out = None
    match language:
        case "py" | "python":
            out = subprocess.run(
                [language],
                shell=True,
                input=code.encode("utf-8"),
                capture_output=True,
            )
        case "sh" | "fish" | "bash" | "shell":
            out = subprocess.run(
                [language],
                shell=True,
                input=code.encode("utf-8"),
                capture_output=True,
            )
        case "local":
            out = globals()[code]
        case _:
            print("This language is not supported yet")
    if isinstance(out, subprocess.CompletedProcess) and not std_out:
        out = out.stdout.decode("utf-8")
    return out
