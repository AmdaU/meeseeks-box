import subprocess

def execute_code(language, code):
    match language:
        case 'py' | 'python':
            subprocess.run([language], shell=True, input=code.encode('utf-8'))
        case 'sh' | 'fish' | 'bash' | 'shell':
            subprocess.run([language], shell=True, input=code.encode('utf-8'))
        case _:
            print("This language is not supported yet")
