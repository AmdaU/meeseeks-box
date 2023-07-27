from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from argparse import ArgumentParser
import parser
from backends import gpt
import custom_logging as log
from config import script_dir, presets, warnings_at_launch_enabled, tips_enabled
from gpt_functions import get_images, show_image, wait, shell_command,\
    google_search, read_web_page
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion import WordCompleter

completer = WordCompleter(['/exit', '/clear', '/reset', '/get', '/set'])

completer = NestedCompleter.from_nested_dict({
    '/exit': None,
    '/clear': None,
    '/reset': None,
    '/set': {
        "model": {"\"gpt-4\"", "\"gpt-3.5-turbo\""},
        "temp": None},
    '/get': {"discussion", "temp", "model"},
    '/save': None,
    '/exec':None,
    '/md': None,
    '/help': None
})

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
    help='"Live" preview alows the anwser to be seen as it is being generated'
         '(experimental)',
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
    help="enable mutiline input"
         "(`meta+enter` or `Esc` than `enter` to submit)",
    default=False,
    action="store_true",
)

args = arg_parser.parse_args()

if tips_enabled:
    log.system("tip: use /help or /? to get information on available commands")
if warnings_at_launch_enabled:
    if args.live:
        log.system("Live feature is experimental, expect buginess")
    if args.action:
        log.danger(
            "Terminal acces is still experimental,"
            "giving acces to your terminal to chat gpt might be very dangerous!"
        )

live = args.live

functions = [get_images, show_image, wait, shell_command,
             google_search, read_web_page]

# initiate meeseeks instance
meeseeks = gpt(
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
        content_user = prompt("›",
                              history=history,
                              multiline=args.multiline,
                              completer=completer
                              )
        if not len(content_user):
            pass

        elif content_user[0] == "/":
            parser.command(content_user, meeseeks=meeseeks,
                           code_blocks=code_blocks)
            continue

        else:
            meeseeks.tell(content_user)

    content_assistant = meeseeks.reply(action_mode=args.action)
