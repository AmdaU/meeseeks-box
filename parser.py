import re
import subprocess
import sys

code_block = r"`{3}(?P<language>[\w+#-]+) ?\n(?P<code>[\s\S]+)\n`{3}"


def code(string):
    match = re.finditer(code_block, string)

    matches = list(match)
    if len(matches) == 0:
        return string, None

    new_text = re.sub(code_block, "\g<0>\n this is code :)", string)

    return new_text, [match.groups() for match in matches]


def command(command, meeseeks=None):
    if not command[0] == '/':
        raise(Exception('This function should not have been called...'))
    command_args = command[1:].split(' ')
    command_name = command_args.pop(0)

    def ensure_meeseeks(name):
        if not meeseeks:
            print('No meeseeks was given, cannot "{name}"')
        return bool(meeseeks)

    match command_name:
        case 'exit':
            sys.exit(0)
        case 'save':
            if ensure_meeseeks(command_name):
                meeseeks.save_discussion()
        case 'remember':
            if ensure_meeseeks(command_name):
                meeseeks.remember(' '.join(command_args))
        case 'set':
            if ensure_meeseeks(command_name):
                setattr(meeseeks, command_args[0], eval(command_args[1]))
        case 'get':
            if ensure_meeseeks(command_name):
                attr = getattr(meeseeks, command_args[0])
                print(attr)
        case 'title':
            if ensure_meeseeks(command_name):
                meeseeks.title()
        case _:
            print('this command doesn\'t exist')
