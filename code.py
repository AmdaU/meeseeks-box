import subprocess

def execute_code(language, code):
    out = None
    match language:
        case 'py' | 'python':
            out = subprocess.run([language], shell=True, input=code.encode('utf-8'), capture_output=True)
        case 'sh' | 'fish' | 'bash' | 'shell':
            out =subprocess.run([language], shell=True, input=code.encode('utf-8'), capture_output=True)
        case _:
            print("This language is not supported yet")
    return out
