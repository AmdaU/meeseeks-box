from code import execute_code
import custom_logging as log
from duckduckgo_search import DDGS
from itertools import islice
import json
from spinner import loading_animation_dec
import subprocess
from time import sleep


def show_image(path: str = None, img_url: str = None):
    "Show the image located at `path` or at the image's full url `img_url`)"
    if path:
        log.system("showing image, path=", path)
        subprocess.run(f"kitty +kitten icat {path}", shell=True)
    elif img_url:
        log.system(f"showing image, url={img_url}")
        subprocess.run(f"curl -s '{img_url}' | kitty icat", shell=True)

    return "**image**"


def wait(n: int):
    "wait for n seconds"
    sleep(n)
    return 'wait over'


def google_search(query: str, num_results: int = 4):
    """Return the results of a google search with their url"""
    log.system(f'searching for {query} ...')
    search_results = []
    results = DDGS().text(query)
    for item in islice(results, num_results):
        search_results.append(item)

    return json.dumps(search_results, ensure_ascii=False, indent=4)


def get_images(url: str):
    "gets the all the images urls from a web page"
    from bs4 import BeautifulSoup
    import requests

    log.system(f'scrapping {url} ...')

    # Make a request to the webpageurl
    response = requests.get(url)

    # Create a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')
    urls = [img.get('src') for img in img_tags]

    return [url for url in urls if url is not None]


def read_web_page(url: str):
    """returns the text content of a webpage from a url"""
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
    readable_text = [element.strip()
                     for element in text_elements if element.parent.name in
                     (['div', 'p', ] + [f'h{n}' for n in range(1, 7)])]

    # Join the text elements into a single string
    readable_text = ' '.join(readable_text)

    return readable_text


def list_steps(steps: list[str]):
    "Make a list of necessary step in order to run a complex task"
    log.system(f"steps: {steps}")


@loading_animation_dec(
    text="running `{}`",
    text_format=["args[0].split('\\n')[0]"
                 "+('...' if len(args[0].split('\\n')) > 1 else '')"],
    trace="ran `{}`",
    trace_format=["args[0]"])
def shell_command_real(command: str):
    "executes the given shell command in bash as is"

    out = execute_code("bash", command, std_out=True)

    # returns sdtout and stderr to chatgpt
    out_str = out.stdout.decode("utf-8")
    err_str = out.stderr.decode("utf-8")
    if err_str == "" and out_str == "":
        out = "Command was run succesfully!"
    elif err_str == "" or out_str == "":
        out = out_str + err_str
    else:
        out = out_str + '\n' + err_str

    return out


def shell_command(command: str):
    "executes the given shell command in bash as is"
    return shell_command_real(command)
