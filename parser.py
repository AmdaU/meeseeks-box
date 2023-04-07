import re
import subprocess
import sys


def code(markdown_string:str) -> tuple[str, list[tuple]]:
    '''
    Identifies markdown code blocks and tags them with a number.
    Returns the annotated markdown and a list of the code block in the format:
    (language, code)
    '''
    # regex pattern of a code cell
    code_block = r"(```(?P<language>[\w+#-]+?)? ?\n(?P<code>(?![\s\S]```[\s\S])[\s\S]+?)?\n)```"

    matches = list(re.finditer(code_block, markdown_string))

    # if there is no code cell, return unmodified markdown
    if len(matches) == 0:
        return markdown_string, None

    # counter for the numbers of cells
    count = iter(range(len(matches)))

    def append_cell_number(match):
        return match.groups()[0] + f'\n[{next(count)}]\n```'

    new_text = re.sub(code_block, append_cell_number, markdown_string)

    return new_text, [match.groups()[1:] for match in matches]


def command(command: str, meeseeks=None) -> None:
    '''Parses user commands'''
    # raw string (with /) should be passed
    if not command[0] == '/':
        raise(Exception('This function should not have been called...'))
    command_args = command[1:].split(' ')
    command_name = command_args.pop(0)

    # most commands (even if not all) require a that a meeseeks was passed
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
        case 'code':
            pass
        case _:
            print('this command doesn\'t exist')
