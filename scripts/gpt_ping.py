from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from argparse import ArgumentParser
from code import execute_code
import parser
from backends import gpt35
import custom_logging as log
from config import script_dir, presets
from time import sleep
from datetime import datetime
from duckduckgo_search import DDGS
import json
from itertools import islice
from fancy_print import loading_animation
from colorama import Fore, Style


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
    """Return the results of a google search with their url"""
    log.system(f'searching for {query} ...')
    search_results = []
    results = DDGS().text(query)
    for item in islice(results, num_results):
        search_results.append(item)

    return json.dumps(search_results, ensure_ascii=False, indent=4)

def read_web_page(url:str):
    """returns the content of a webpage from a url"""
    from bs4 import BeautifulSoup
    import requests

    log.system(f'reading {url} ...')

    # Make a request to the webpageurl
    response = requests.get(url)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the text elements in the webpage
    text_elements = soup.find_all(string=True)

    # Filter out unwanted elements like scripts and styles
    readable_text = [element.strip() for element in text_elements if element.parent.name in
    (['div', 'p', ] + [f'h{n}' for n in range(1, 7)])]

    # Join the text elements into a single string
    readable_text = ' '.join(readable_text)

    return readable_text

def list_steps(steps: list[str]):
    "Make a list of necessary step in order to run a complex task"
    log.system(f"steps: {steps}")

def shell_command(command:str):
    "executes the given shell command in bash as is"
    # trims the command to a signle line since loading animation only suppots
    # singles lines
    command_lines = command.split('\n')
    command_str= command_lines[0] + "..."*(len(command_lines) > 1)

    # executes the command (with animation)
    args = {"language": "bash", "code": command, "std_out": True}
    out = loading_animation(f"running `{command_str}` ...", execute_code, args)

    # confirms the command has been run
    print(f'{Fore.GREEN}⣿{Style.RESET_ALL} ran `{command_str}`')

    # returns sdtout and stderr to chatgpt
    out_str = out.stdout.decode("utf-8")
    err_str = out.stderr.decode("utf-8")
    if err_str == "" and out_str == "":
        out = "Command was run succesfully!"
    elif err_str == "" or out_str == "":
        out = out_str + err_str
    else:
        out = out_str + '\n' + err_str

    # log.command(f'output was:\n{out}')
    return out

functions = [test, wait, shell_command, google_search, list_steps, read_web_page]

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

