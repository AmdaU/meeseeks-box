import subprocess
import platform
import parser
from config import script_dir

style_file = "ressources/style.json"


# print the output so that it is  ✨ p r e t t y ✨
def fancy_print(content):
    global terminal_height, terminal_width
    fancy_out = subprocess.run(
        [f"glow -s '{script_dir}/{style_file}' -w {terminal_width}"],
        shell=True,
        input=(content).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return fancy_out.stdout.decode("utf-8")


def print_stream(content):
    parsed_content, _ = parser.code(content)  # parse the whole code every time

    fancy_string = fancy_print(parsed_content)

    lines = fancy_string.split("\n")
    lines_num = len(lines)

    # Number of lines to be overiden by new print
    amount_to_print = min(terminal_height - 3, lines_num)
    global last_lines_num
    number_of_new_lines = lines_num - last_lines_num
    amount_to_erase = amount_to_print - (number_of_new_lines)

    # overides previous lines
    if amount_to_erase:
        print(f"\033[{amount_to_erase}A", end="\r")
    for line in lines[-amount_to_print:]:
        print(line)

    last_lines_num = lines_num


def init_print():
    global terminal_height, terminal_width
    global last_lines_num
    terminal_height, terminal_width = get_terminal_dimentions()
    last_lines_num = 0


def get_terminal_dimentions():
    os = platform.system()
    match os:
        case "Linux":  # Probably works on macos as well but needs testing
            out_stty = subprocess.run(
                ["stty size"], shell=True, capture_output=True
            )
            terminal_height, terminal_width = out_stty.stdout.decode().split(
                " "
            )
        case _:
            print(f"live printing on {os} is not currently supported")
    return int(terminal_height), int(terminal_width)


def terminal_dims_windows():  # not tested yet
    import ctypes

    STD_OUTPUT_HANDLE = -11
    h = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    csbi = ctypes.create_string_buffer(22)
    res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

    if res:
        import struct

        (
            bufx,
            bufy,
            curx,
            cury,
            wattr,
            left,
            top,
            right,
            bottom,
            maxx,
            maxy,
        ) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        width = right - left + 1
        height = bottom - top + 1
        return height, width
    else:
        print("Error getting console screen buffer info")
