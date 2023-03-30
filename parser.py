import re
import subprocess

code_block = r"`{3}(?P<language>.+)\n(?P<code>[\s\S]+)\n`{3}"


def parse_code(string):
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
            subprocess.run([code], shell=True)
