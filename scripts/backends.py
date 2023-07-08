import json
import subprocess
from datetime import datetime
from functools import lru_cache
import openai
import parser
from fancy_print import init_print, print_stream, print_latex, fancy_print
from spinner import loading_animation_dec
from collections import OrderedDict
import custom_logging as log
from code import execute_code
from config import script_dir
from colorama import Fore
from typing import Generator
from time import sleep
from threading import ThreadError
from os import _exit as exit

class Meeseeks:
    def __init__(
        self,
        temp: int = 1,  # temprature of the llm
        length: int = 100,  # maximum token in reply
        timeout: int = 10,  # maximum time to reply
        preset: str = "default",  # preset
        discussion: list = None,  # overides the preset with a custom discussion
        live: bool = False,  # If live printing is enabled
    ):
        self.archive = OrderedDict()  # Ordered so the title is first
        self.archive_file = None
        self.name = "Meeseeks"
        self.notes = []
        self.temp = temp
        self.length = length
        self.timeout = timeout
        self.live = live

        # preset argument will be overident by discussion
        if discussion:
            self.discussion = discussion
        else:
            self.load_preset(preset)

    def reply(
        self,
        message: str | list = None,
        keep_reply: bool | None = None,
        action_mode: bool = False,
    ) -> tuple[str, str | None]:
        """
        This method is the most important for a meeseeks as it is the one
        who actually request a reply from the llm. The specific details for
        requesting a reply are in `self.get_response`. Outputs the (reply, action)
        """
        # additional message will not be remembered in the meeseeks memory
        # if you want it to be remembered, use `.tell()` instead
        discussion = self.discussion.copy()
        if isinstance(message, dict):
            discussion.append(message)
        elif isinstance(message, list):
            discussion.extend(message)

        # Unless specified, reply is not kept if an additional message is
        # passed
        if keep_reply is None:
            keep_reply = not message

        if keep_reply:
            init_print()  # sets text width and rests last_line_num

        content_assistant = None
        parsed_content = None

        response = self.get_response(live=self.live, discussion=discussion)
        if self.live:
            content_assistant = ""  # the return message
            # loops over the stream in real time as the chunks comme in
            for chunk in response:
                content_assistant += chunk
                parsed_content, _ = parser.code(content_assistant)  # parse the whole code every time
                parsed_content, latex_groups = parser.latex(parsed_content)
                if latex_groups:
                    print_stream(parsed_content.split('latex_dummy')[0])
                    print(f"\033[F"*2)
                    print(f"\033[K"*2)
                    print_latex(latex_groups[0])
                    init_print()
                    content_assistant = ''

                elif keep_reply and content_assistant:
                    print_stream(parsed_content)  # Print content as it come

        else:
            content_assistant = response
            parsed_content = content_assistant
            if content_assistant and keep_reply:
                parsed_content, code_blocks = parser.code(parsed_content)
                parsed_content, latex_blocks = parser.latex(parsed_content)
                if latex_blocks:
                    for i, text_part in enumerate(content_assistant.split('latex_dummy')):
                        print(fancy_print(text_part))
                        if i < len(latex_blocks):
                            print_latex(latex_blocks[i])
                elif content_assistant:
                    print(fancy_print(parsed_content))


        # adds the reply to the discussion
        if keep_reply and content_assistant:
            message = {"role": "assistant", "content": content_assistant}
            self.discussion.append(message)

        return parsed_content

    def tell(self, message: str, role: str = "user"):
        """adds a message to the meeseeks mid-term memory"""
        message_user = {"role": role, "content": message}
        self.discussion.append(message_user)

    def save_discussion(self):
        """saves the current discussion along with other info to a file"""
        self.archive["title"] = self.title
        if not self.archive_file:
            # the filename is simply the current time, which isn't a great name
            filename = str(datetime.now()).replace(" ", "_")
            self.archive_file = f"{script_dir}/archive/{filename}.json"
            log.system(
                f"The discussion has ben saved to archive/{filename}.json",
            )
        else:
            log.system(
                "savefile has been updated",
            )
        self.archive["discussion"] = self.discussion
        self.archive["notes"] = self.notes
        with open(self.archive_file, "w+") as file:
            file.write(json.dumps(self.archive, indent=4))

    def create_new_Meeseeks(self):
        pass

    def load_preset(self, preset_name):
        """Sets up the "preset", aka info before the discussion starts"""
        # Loading the preset info from the json file

        def get_data(process: dict) -> str:
            out = process["content"]
            if "data" in process:
                for key, subprocess_ in process["data"].items():
                    result = get_data(subprocess_)
                    out = out.replace("{" + str(key) + "}", result)

            if "exec" in process:
                out = execute_code(process["exec"], out)

            return out

        # loads prestes from preset file
        presets = {}
        with open(f"{script_dir}/ressources/presets.json") as read:
            presets = json.load(read)
        preset_list = list(presets)

        if preset_name not in preset_list:
            log.system(
                f"The preset `{preset_name}` does not exist, using default"
            )
            preset_name = "default"

        preset = presets[preset_name]

        self.discussion = []
        for message in preset["prompt"]:
            message["content"] = get_data(message)
            if "data" in message:
                del message["data"]
            self.discussion.append(message)

    def remember(self, specific=None):
        """store information the long term memory"""
        if not specific:
            specific = "the current whole conversation"

        message = {
            "role": "system",
            "content": "You shall now try to summarize something that"
            "was mentioned in this conversation. Make it concise but"
            "clear. It will later be used to remind you of what happend"
            "in the conversation. Use key points if you have to. The"
            "information does **not** need to be clear to a human,"
            f"**only** to you. The subject of your note is: {specific}",
        }
        note = self.reply(message)
        self.notes.append(note)
        log.system(f"{self.name} has taken note of {specific}\nNote: {note}")

    @property
    @lru_cache()  # Once generated, the title stays
    def title(self):
        """gives a title to the current discussion"""
        # temporarily sets it's temperature to 0 for les "messy" result
        old_temp = self.temp
        self.temp = 0
        message = {
            "role": "system",
            "content": "give a short title to this conversation."
            "Do not provide **any** explanation or aditional content."
            "Do not give **any** formating like 'Title:' or similar."
            "Do not end with a dot.",
        }
        title = self.reply(message)

        self.temp = old_temp  # resets the temperature
        return title


# gpt 3.5 backend -------------------------------------------------------------
class gpt(Meeseeks):
    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        api_key: str | None = None,
        max_number_of_tries: int = 3,
        temp: int = 1,
        length: int = 100,
        timeout: int = 10,
        preset: str = "default",
        discussion: list = None,
        live: bool = False,
        functions = None,
        model = "gpt-3.5-turbo"
    ):
        super(gpt, self).__init__(
            temp, length, timeout, preset, discussion, live
        )  # inherits from Meeseeks init

        self.model = model
        # Loads open ai api key
        if api_key is None:
            from config import open_ai_key as api_key

            if api_key in ["", "<your-open-ai-api-key>"]:
                log.error(
                    "In order to use the gpt 3.5 model, you need to set your api_key in `paramters.dat`"
                )
                exit(1)

        self.api_key = api_key

        self.max_number_of_tries = max_number_of_tries  # does nothing currently
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.functions_json = list(map(parser.function_to_gpt_json, functions))
        self.functions = {func.__name__: func for func in functions}

    def get_response(self, live: bool, discussion: list) -> str | Generator:
        # sends the rely request using the openai package
        openai.api_key = self.api_key
        kwargs = {
            "model": self.model,
            "messages": discussion,
            "temperature": self.temp,
            "max_tokens": self.length,
            "stream": self.live,
            "functions": self.functions_json
        }

        @loading_animation_dec("Waiting {}s before retry...", text_format=["args[0]"])
        def custom_sleep(seconds):
            sleep(seconds)

        @loading_animation_dec("Waitting for open ai's response", trace_failed="{}", trace_format_failed={"type(Ex).__name__"}, trace_color=Fore.YELLOW)
        def git_it(**kwargs):
            return openai.ChatCompletion.create(**kwargs)

        n_tries = 0
        response = None
        while (n_tries := n_tries + 1) <= 3 and response==None:
            response = git_it(**kwargs)
            sleep(1)
            # custom_sleep(5)

        if n_tries == 4:
            exit(1)

        if self.live:

            def response_content():
                function_name, function_args = '', ''
                for chunk in response:
                    content = chunk["choices"][0]["delta"]
                    if content.get("function_call"):
                        if content['function_call'].get('name'):
                            function_name += content['function_call'].get('name')
                        function_args += content['function_call']['arguments']
                    else:
                        chunk_out = content.get("content", "")
                        yield chunk_out
                if function_name != '':
                    output = str(self.functions[function_name](**eval(function_args)))
                    self.discussion.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "function_call": {
                                'name': function_name,
                                'arguments': function_args
                            }
                        }
                    )
                    self.discussion.append(
                        {
                            "role": "function",
                            "name": function_name,
                            "content": output,
                        })
                    return None

            return response_content()

        else:
            message = response["choices"][0]["message"]
            if message.get("function_call"):
                name, args = message['function_call'].values()
                # print(f'calling {name} with argument {args}')
                output = str(self.functions[name](**eval(args)))
                message.content = None
                message['function_call'] = message['function_call'].to_dict()
                self.discussion.append(message.to_dict())
                self.discussion.append(
                    {
                        "role": "function",
                        "name": name,
                        "content": output,
                    })
                return None
            return message["content"]


class llama(Meeseeks):
    pass
