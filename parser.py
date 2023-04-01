import re
import subprocess
import sys

code_block = r"`{3}(?P<language>.+)\n(?P<code>[\s\S]+)\n`{3}"


def code(string):
    match = re.finditer(code_block, string)

    matches = list(match)
    if len(matches) == 0:
        print("found no code cells")
        return

    if len(matches) > 1:
        print("found multiple code cell, will only consider last one")

    match = matches[-1]

    language, code = match.groups()

    execute = input(f'System: a {language} code cell was found,'
                    'would you like to execute it? (y/N)')

    if execute.lower() not in ['y', 'yes']:
        return

    match language:
        case 'py' | 'python':
            exec(code)
        case 'sh' | 'fish' | 'bash' | 'shell':
            subprocess.run([f'{language} -c "{code}"'], shell=True)
        case _:
            print("This language is not supported yet")


def command(command):
    if not command[0] == '/':
        raise(Exception('This function should not have been called...'))
    match command[1:].split(' ')[0]:
        case 'exit':
            sys.exit(1)
        case 'save':
            pass
        case 'remember':
            pass
        case _:
            print('this command doesn\'t exist')
