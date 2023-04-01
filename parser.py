import re
import subprocess
import sys

code_block = r"`{3}(?P<language>[\w\W]+).*\n(?P<code>[\s\S]+)\n`{3}"


def code(string):
    match = re.finditer(code_block, string)

    matches = list(match)
    if len(matches) == 0:
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
    command_args = command[1:].split(' ')
    command_name = command_args.pop(0)
    match command_name:
        case 'exit':
            sys.exit(0)
        case 'save':
            pass
        case 'remember':
            pass
        case 'set':
            pass
        case _:
            print('this command doesn\'t exist')
