from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from argparse import ArgumentParser
from code import execute_code
import parser
from backends import gpt35
import custom_logging as log
from config import script_dir, presets
from fancy_print import fancy_print


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

# initiate meeseeks instance
meeseeks = gpt35(
    preset=args.preset,
    discussion=args.message,
    length=args.response_length,
    temp=args.temperature,
    live=live,
)
code_blocks = None
action = "USER"
failure_counter = 0

# Main discussion loop --------------------------------------------------------
while True:
    match action:
        case "USER":
            failure_counter = 0
            if (
                content_user := prompt(
                    "> ", history=history, multiline=args.multiline
                )
            )[0] == "/":
                parser.command(
                    content_user, meeseeks=meeseeks, code_blocks=code_blocks
                )
                continue
            meeseeks.tell(content_user)
            action = "ACTION"
            continue

        case "ACTION":
            content_assistant, action = meeseeks.reply(action_mode=args.action)

        case None:
            failure_counter = 0
            content_assistant, code_blocks = parser.code(content_assistant)

            if not meeseeks.live:
                fancy_print(content_assistant)
            action = "USER"

        case "LIST":
            print(content_assistant)
            meeseeks.tell("You shall now do the first point", role="system")

        case "COMMAND":
            failure_counter = 0
            log.system(f"Running command `{content_assistant}`")
            out = execute_code("sh", content_assistant, std_out=True)
            out_str = parser.terminal_output(out, meeseeks.model)
            meeseeks.tell("output was:" + out_str, role="system")
            action = "ACTION"

        case _:
            meeseeks.tell(
                "You did not pick a valid action. You must **ALWAYS** reply in the form `ACTION:content` by picking from one the following actions; COMMAND, USER",
                role="system",
            )
            log.system(f"Internal error, retring, (action = {action})")
            log.system(f"assitant tried to say: '{content_assistant}'")
            failure_counter += 1
            if failure_counter > 2:
                action = "USER"
                continue
            action = "ACTION"
