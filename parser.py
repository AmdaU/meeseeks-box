import re
import sys

code_block = r"`{3}(?P<language>.*)\n(?P<code>[\s\S]+)\n`{3}"


def parse_code(string):
    match = re.search(code_block, string)
    if not match:
        return
    else:
        print(match.groups())
    if match.groups()[0] in ['py', 'python']:
        print('python detected: executing code:')
        exec(match.groups()[1])
