import json
import subprocess
from datetime import datetime
from functools import lru_cache
import openai
import parser
from fancy_print import init_print, print_stream
from collections import OrderedDict
import custom_logging as log
from code import execute_code
from config import script_dir
from sys import exit
from typing import Generator


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
        action = None
        looking_for_action = action_mode

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

        response = self.get_response(live=self.live, discussion=discussion)

        if self.live:
            content_assistant = ""  # the return message
            content_parsed = ""
            # loops over the stream in real time as the chunks comme in
            for chunk in response:
                content_assistant += chunk
                content_parsed += chunk
                # extract the current action from the text
                if looking_for_action:
                    content_parsed, action = parser.action(content_assistant)
                    if (action is not None) or (len(content_assistant) > 10):
                        log.system(f"action is {action}")
                        looking_for_action = False

                if keep_reply and action is None and not looking_for_action:
                    print_stream(content_parsed)  # Print content as it come

        else:
            content_assistant = response
            content_parsed = content_assistant

        # adds the reply to the discussion
        if keep_reply:
            message = {"role": "assistant", "content": content_assistant}
            self.discussion.append(message)

        return content_parsed, action

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
            content = json.dumps(self.archive)
            formated = subprocess.run(
                ["jq"],
                shell=True,
                capture_output=True,
                input=content.encode("utf-8"),
            ).stdout.decode()
            file.write(formated)

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
        note, _ = self.reply(message)
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
        title, _ = self.reply(message)

        self.temp = old_temp  # resets the temperature
        return title


# gpt 3.5 backend -------------------------------------------------------------
class gpt35(Meeseeks):
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
    ):
        super(gpt35, self).__init__(
            temp, length, timeout, preset, discussion, live
        )  # inherits from Meeseeks init

        self.model = "gpt-3.5-turbo"
        # Loads open ai api key
        if api_key is None:
            from config import open_ai_key as api_key

            if api_key == "":
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

    def get_response(self, live: bool, discussion: list) -> str | Generator:
        # sends the rely request using the openai package
        openai.api_key = self.api_key

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=discussion,
            temperature=self.temp,
            max_tokens=self.length,
            stream=self.live,
        )
        if self.live:

            def response_content():
                for chunk in response:
                    yield chunk["choices"][0]["delta"].get("content", "")

            return response_content()

        else:
            return response["choices"][0]["message"]["content"]


class llama(Meeseeks):
    pass
