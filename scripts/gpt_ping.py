from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from argparse import ArgumentParser
from code import execute_code
import parser
from backends import gpt35
import custom_logging as log
from config import script_dir, presets
from fancy_print import fancy_print
from time import sleep
from datetime import datetime
from duckduckgo_search import DDGS
import json
from itertools import islice

# Get the path to the directory were this file is located
history = FileHistory(f"{script_dir}/log/history.txt")
# Argument parsing ------------------------------------------------------------
preset_list = list(presets)

# Parses the command line arguments
arg_parser = ArgumentParser()

arg_parser.add_argument(
    "preset",
    help=f"Preset of the assistance. Can be one of: {preset_list}",
    default="default",
    nargs="?",
)
arg_parser.add_argument(
    "-p",
    help="If used, the program will not run in interactive mode, only the",
    type=str,
)
arg_parser.add_argument("-T", "--temperature", type=float, default=0)
arg_parser.add_argument(
    "--live",
    help='"Live" preview alows the anwser to be seen as it is being generated (experimental)',
    action="store_true",
)
arg_parser.add_argument("-b", "--backend", type=str, default="gpt3.5")
arg_parser.add_argument(
    "-t", help="response timeout (seconds)", type=int, default=10
)
arg_parser.add_argument(
    "-l",
    "--response_length",
    help="Maximum number of tokens",
    type=int,
    default=200,
)
arg_parser.add_argument(
    "-m", "--message", help="override preset and send message", type=str
)
arg_parser.add_argument(
    "--action",
    help="action mode",
    default=False,
    action="store_true",
)
arg_parser.add_argument(
    "--multiline",
    help="enable mutiline input (`meta+enter` or `Esc` than `enter` to submit)",
    default=False,
    action="store_true",
)

args = arg_parser.parse_args()


log.system("tip: use /help or /? to get information on available commands")
if args.live:
    log.system("Live feature is experimental, expect buginess")
if args.action:
    log.danger(
        "Terminal acces is still experimental, giving acces to your terminal to chat gpt might be very dangerous!"
    )

live = args.live

def test(test_sentence:str):
    "this function runs tests!"
    print(f"THIS IS A TEST: {test_sentence}")
    return 'test succesfull'

def wait(n:int):
    "wait for n seconds"
    sleep(n)
    return 'wait over'

def google_search(query:str, num_results:int=4):
    """Return the results of a google search"""
    log.system(f'searching for {query} ...')
    search_results = []
    results = DDGS().text(query)
    for item in islice(results, num_results):
        search_results.append(item)

    return json.dumps(search_results, ensure_ascii=False, indent=4)

# def time():
    # "gets the current time"
    # return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def list_step(hello:list[str]):
    "plan a list of action to do and goes through them one a time"
    pass

def shell_command(command:str):
    "executes the given shell command in bash as is"
    log.system(f'running `{command}` ...')
    out = execute_code(
        "bash", command, std_out=True
    )
    out_str = out.stdout.decode("utf-8")
    err_str = out.stderr.decode("utf-8")
    log.system(f'output was:\n{out_str}\n{err_str}')
    return out_str + '\n' + err_str


functions = [test, wait, shell_command, google_search, list_step]



# initiate meeseeks instance
meeseeks = gpt35(
    preset=args.preset,
    discussion=args.message,
    length=args.response_length,
    temp=args.temperature,
    live=live,
    functions=functions
)
code_blocks = None

content_assistant = 'dummy'

# Main discussion loop --------------------------------------------------------
while True:
    if content_assistant:
        content_user = prompt("> ",
                                history=history,
                                multiline=args.multiline
                                )
        if content_user[0] == "/":
            parser.command(content_user, meeseeks=meeseeks,
                            code_blocks=code_blocks)
            continue

        meeseeks.tell(content_user)

    content_assistant = meeseeks.reply(action_mode=args.action)

    if content_assistant and not meeseeks.live:
        content_assistant, code_blocks = parser.code(content_assistant)
        print(fancy_print(content_assistant))

