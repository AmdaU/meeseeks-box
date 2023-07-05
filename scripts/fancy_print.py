import subprocess
import platform
from config import script_dir, enable_latex_to_png
from colorama import Fore, Style
from time import sleep
from collections.abc import Callable
import threading
import io
import sys

style_file = "ressources/style.json"

# print the output so that it is  ✨ p r e t t y ✨
def fancy_print(content):
    global terminal_height, terminal_width
    fancy_out = subprocess.run(
        [f"glow -s '{script_dir}/{style_file}' -w {terminal_width -4}"],
        shell=True,
        input=(content).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return fancy_out.stdout.decode("utf-8")


def print_stream(content):
    fancy_string = fancy_print(content)

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
        case "Linux" | "Darwin":
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


def latex2png(latex: str):
    import matplotlib.pyplot as plt
    from PIL import Image, ImageChops
    import numpy as np
    plt.rc('text', usetex=True)
    plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}' +\
                                        '\n'+r'\usepackage{physics}'

    def trim(im, border):
        bg = Image.new(im.mode, im.size, border)
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    fig, ax = plt.subplots()
    fig.set_size_inches(20, 3)
    ax.annotate(latex, (0,0), fontsize=20, ha='center', va='center', color='w')
    ax.axis('off')
    plt.autoscale('tight')
    fig.patch.set_alpha(0)
    ax.set_facecolor((0,0,0,0))

    fig.canvas.draw()
    rgba_buffer = np.array(fig.canvas.renderer.buffer_rgba())
    pil_image = Image.fromarray(rgba_buffer)
    cropped_image = trim(pil_image, '#00000000')

    cropped_image.save(f'{script_dir}/temp/latex.png')

def print_latex(latex:str):
    """
    Renders latex code. If `enable_latex_to_png` is enabled in parameters.dat
    the code is rendered using latex and kitty icat if not it uses pylatexenc
    """
    if enable_latex_to_png:
        latex2png(latex)
        subprocess.run(f"kitty +kitten icat {script_dir}/temp/latex.png", shell=True)
    else:
        from pylatexenc.latex2text import LatexNodes2Text
        print(LatexNodes2Text().latex_to_text(latex))

def loading_animation(loading_text:str, task:Callable, args:list = [], kwargs:dict = {},
                      animation = "⣾⣽⣻⢿⡿⣟⣯⣷", color = Fore.BLUE):
    """
    Make a loading animation while `task` runs with `args` as arguments
    """
    # declare a wrapper function that stores the result of the function
    result = []
    def meta():
        result.append(task(*args, **kwargs))

    loading_text = loading_text.split('\n')[0]

    # create the thead
    thread = threading.Thread(target=meta)
    thread.start()

    # Prints loading animation + loading_text until task is over
    i = 0
    while thread.is_alive():
        print(f'\r{color}{animation[i % len(animation)]}'
              f'{Style.RESET_ALL} ' + loading_text, end="")
        sleep(0.1)
        i+=1

    #delete message when done
    print(f"\033[2K", end="\r")

    # just making sure
    thread.join()

    return result[0]

# def loading_animation_dec(text, animation= "⣾⣽⣻⢿⡿⣟⣯⣷", color = Fore.BLUE, text_format = None, capture_output=True):
    # def decorator(task):
        # def wrapper(*args, **kwargs):
            # """
            # Make a loading animation while `task` runs with `args` as arguments
            # """

            # if text_format:
                # values = []
                # for i in text_format:
                    # values.append(eval(i))

                # loading_text = text.format(*values)
            # else:
                # loading_text = text

            # # declare a wrapper function that stores the result of the function
            # result = []
            # def meta():
                # result.append(task(*args, **kwargs))

            # loading_text = loading_text.split('\n')[0]

            # if capture_output:
                # output = io.StringIO()
                # sys.stdout = output

            # # create the thead
            # thread = threading.Thread(target=meta)
            # thread.deamon = True
            # thread.start()

            # sys.stdout = sys.__stdout__
            # # Prints loading animation + loading_text until task is over
            # i = 0
            # while thread.is_alive():
                # print(f'\r{color}{animation[i % len(animation)]}'
                    # f'{Style.RESET_ALL} ' + loading_text, end="")
                # sleep(0.1)
                # i+=1

            # #delete message when done
            # print(f"\033[2K", end="\r")

            # # just making sure
            # thread.join()
            # sys.stdout = sys.__stdout__


            # return result[0] if len(result) else None

        # return wrapper
    # return decorator

def loading_animation_dec(text, animation= "⣾⣽⣻⢿⡿⣟⣯⣷", color = Fore.BLUE, text_format = None, capture_output=True):
    def decorator(task):
        def wrapper(*args, **kwargs):
            """
            Make a loading animation while `task` runs with `args` as arguments
            """

            if text_format:
                values = []
                for i in text_format:
                    values.append(eval(i))

                loading_text = text.format(*values)
            else:
                loading_text = text

            loading_text = loading_text.split('\n')[0]

            kill_animation = threading.Event()
            def animate():
                """Prints loading animation + loading_text until task is over"""
                i = 0
                print()
                print()
                print(f"\033[2A", end="")
                while not kill_animation.is_set():
                    print(f'\r{color}{animation[i % len(animation)]}'
                        f'{Style.RESET_ALL} ' + loading_text, end="")
                    print(f"\033[2B", end="\r")
                    sleep(0.1)
                    print(f"\r\033[2A", end="")
                    i+=1

                #delete message when done
                print(f"\033[2K", end="\r")

            # create the thead
            thread = threading.Thread(target=animate, daemon=True)
            thread.start()

            result = task(*args, **kwargs)

            kill_animation.set()

            thread.join()

            return result

        return wrapper
    return decorator
