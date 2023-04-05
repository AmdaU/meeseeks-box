import subprocess

def execute_code(language, code):
    execute = input(f'System: a {language} code cell was found,'
                    'would you like to execute it? (y/N)')

    if execute.lower() not in ['y', 'yes']:
        return

    match language:
        case 'py' | 'python':
            subprocess.run([language], shell=True, input=code.encode('utf-8'))
        case 'sh' | 'fish' | 'bash' | 'shell':
            subprocess.run([language], shell=True, input=code.encode('utf-8'))
        case _:
            print("This language is not supported yet")
