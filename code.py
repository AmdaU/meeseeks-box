from subprocess import run, CompletedProcess
from config import *

def execute_code(language, code, std_out=False):
    out = None
    match language:
        case "py" | "python":
            out = run(
                [language],
                shell=True,
                input=code.encode("utf-8"),
                capture_output=True,
            )
        case "sh" | "fish" | "bash" | "shell":
            out = run(
                [language],
                shell=True,
                input=code.encode("utf-8"),
                capture_output=True,
            )
        case "local":
            out = globals()[code]
        case _:
            print("This language is not supported yet")
    if isinstance(out, CompletedProcess) and not std_out:
        out = out.stdout.decode("utf-8")
    return out
