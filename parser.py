import re
from subprocess import run, CompletedProcess
from sys import exit
from code import execute_code
import custom_logging as log
from tiktoken import get_encoding
from fancy_print import fancy_print
from config import script_dir
from os import system

clear = lambda: system("clear")


def token_count(string: str, model: str):
    encoding = get_encoding(model)
    return len(encoding.encode(string))


def code(markdown_string: str) -> tuple[str, list[tuple]]:
    """
    Identifies markdown code blocks and tags them with a number.
    Returns the annotated markdown and a list of the code block in the format:
    (language, code)
    """
    # regex pattern of a code cell
    code_block = r"(```(?P<language>[\w+#-]+?)? ?\n(?P<code>(?![\s\S]```[\s\S])[\s\S]+?)?\n)```"

    matches = list(re.finditer(code_block, markdown_string))

    # if there is no code cell, return unmodified markdown
    if len(matches) == 0:
        return markdown_string, None

    # counter for the numbers of cells
    count = iter(range(len(matches)))

    def append_cell_number(match):
        return match.groups()[0] + f"\n[{next(count)}]\n```"

    new_text = re.sub(code_block, append_cell_number, markdown_string)

    return new_text, [match.groups()[1:] for match in matches]


def command(command_str: str, meeseeks=None, code_blocks=None) -> None:
    """
    User commands can be entered by using `/command [args]` syntax.
    arguments marked with `?` are optional

    The avalible commands are
    exit:                   ends the script
    save:                   saves the current discussion to `archive/`
    remember [?subject]:    Make the meeseeks take a note
    set [variable] [value]: set a proprity of current meesseks (like `temp`)
    get [variable]:         get a proprity of current meesseks (like `temp`)
    exec [cell number]:     execute code cell
    reply:                  force the meeseeks to reply now
    clear:                  clears the screen
    help (same as ?):       print this message
    """
    # raw string (with /) should be passed
    if not command_str[0] == "/":
        raise (Exception("This function should not have been called..."))
    command_args = command_str[1:].split(" ")
    command_name = command_args.pop(0)

    # most commands (even if not all) require a that a meeseeks was passed
    def ensure_meeseeks(name):
        if not meeseeks:
            log.system('No meeseeks was given, cannot "{name}"')
        return bool(meeseeks)

    match command_name:
        case "exit":
            exit(0)
        case "save":
            if ensure_meeseeks(command_name):
                meeseeks.save_discussion()
        case "remember":
            if ensure_meeseeks(command_name):
                meeseeks.remember(specific=" ".join(command_args))
        case "set":
            if ensure_meeseeks(command_name):
                setattr(meeseeks, command_args[0], eval(command_args[1]))
        case "get":
            if ensure_meeseeks(command_name):
                attr = getattr(meeseeks, command_args[0])
                print(attr)
        case "exec":
            out_str = execute_code(
                *code_blocks[int(command_args[0])], std_out=False
            )
            print(out_str)
            meeseeks.tell(out_str, role="system")
        case "reply":
            msg = meeseeks.reply()
            if not meeseeks.live:
                fancy_print(msg)
        case "clear":
            clear()
        case "help" | "?":
            print(command.__doc__)
        case _:
            log.system("this command doesn't exist")


def terminal_output(out: CompletedProcess, model: str, keep_lines: int = 10):
    str_out = out.stdout.decode("utf-8")
    if token_count(str_out, model):
        log.system(
            f"terminal output too long, outputing last {keep_lines} lines"
        )
    new_out = run("tail -n", stdin=out, shell=True)
    return new_out.stdout.decode("utf-8")


def action(gtp_reply: str) -> tuple[str, str]:
    action_pattern = "([A-Z]+):"
    match = re.search(action_pattern, gtp_reply)
    new_text = re.sub(action_pattern, "", gtp_reply)
    return new_text, match.groups()[0] if match else None
