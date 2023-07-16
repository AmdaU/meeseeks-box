import subprocess
import platform
from config import script_dir, enable_latex_to_png

style_file = "ressources/style.json"


# print the output so that it is  ✨ p r e t t y ✨
def fancy_print(content):
    global terminal_height, terminal_width
    fancy_out = subprocess.run(
        [f"glow -s '{script_dir}/{style_file}' -w {terminal_width -5}"],
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
        delete_line(amount_to_erase)
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
    ax.annotate(latex, (0, 0), fontsize=20, ha='center', va='center',
                color='w')
    ax.axis('off')
    plt.autoscale('tight')
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    fig.canvas.draw()
    rgba_buffer = np.array(fig.canvas.renderer.buffer_rgba())
    pil_image = Image.fromarray(rgba_buffer)
    cropped_image = trim(pil_image, '#00000000')

    cropped_image.save(f'{script_dir}/temp/latex.png')


def print_latex(latex: str):
    """
    Renders latex code. If `enable_latex_to_png` is enabled in parameters.dat
    the code is rendered using latex and kitty icat if not it uses pylatexenc
    """
    if enable_latex_to_png:
        latex2png(latex)
        subprocess.run(f"kitty +kitten icat {script_dir}/temp/latex.png",
                       shell=True)
    else:
        from pylatexenc.latex2text import LatexNodes2Text
        print(LatexNodes2Text().latex_to_text(latex))


def delete_line(n):
    for i in range(n):
        print("\033[A", end="")
        print("\r\033[K", end="\r")
