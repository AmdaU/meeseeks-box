import os
import json
import subprocess
import datetime
import functools
import openai
from fancy_print import init_print, print_stream
from collections import OrderedDict
import custom_logging as log


script_dir = os.path.dirname(os.path.realpath(__file__))


class Meeseeks:
    def __init__(self):
        self.archive = (
            OrderedDict()
        )  # The dict is ordered so the title is first
        self.archive_file = None
        self.name = "Meeseeks"
        self.notes = []

    def reply(self, message: str):
        """
        This method is the most important for a meeseeks as it it the one
        who actually request a reply from the llm this method however
        obviously depends on the specif backends and needs to be reimplemented
        every time, this is just a placeholder
        """
        print(self.__class__.__name__, "backend was not implemented yet")

    def tell(self, message: str, role: str = "user"):
        """adds a message to the meeseeks mid-term memory"""
        message_user = {"role": role, "content": message}
        self.discussion.append(message_user)

    def save_discussion(self):
        """saves the current discussion along with other info to a file"""
        self.archive["title"] = self.title
        if not self.archive_file:
            # the filename is simply the current time, which isn't a great name
            filename = str(datetime.datetime.now()).replace(" ", "_")
            self.archive_file = f"{script_dir}/archive/{filename}.json"
            log.system(
                f"The discussion has ben saved to archive/{filename}.json",
            )
        else:
            log.system(
                f"savefile has been updated",
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

        def get_data_element(thing: str | dict):
            if isinstance(thing, dict):
                pass

        presets = {}
        with open(f"{script_dir}/ressources/presets.json") as read:
            presets = json.load(read)
        preset_list = list(presets)

        if preset_name not in preset_list:
            log.system("This preset does not exist, using default")
            preset_name = "default"

        preset = presets[preset_name]

        self.discussion = preset["prompt"]

        # Some presets will pull 'live' data from the system of elsewhere
        if "data" in preset:
            for data_name, data_command in preset["data"].items():
                result = subprocess.run(
                    [data_command], shell=True, capture_output=True
                ).stdout.decode()
                self.discussion[0]["content"] = self.discussion[0][
                    "content"
                ].replace("{" + str(data_name) + "}", result)

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
    @functools.lru_cache()  # Once generated, the title stays
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
class gpt35(Meeseeks):
    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        api_key: str = "",
        max_number_of_tries: int = 3,
        temp: int = 1,
        length: int = 100,
        timeout: int = 10,
        preset: str = "default",
        discussion: list = None,
        live: bool = False,
    ):
        super(gpt35, self).__init__()  # inherits from Meeseeks init
        if api_key == "":
            with open(f"{script_dir}/open_ai.secrets") as secret:
                self.api_key = secret.readline().strip("\n")
        else:
            self.api_key = api_key

        self.max_number_of_tries = max_number_of_tries
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.temp = temp
        self.length = length
        self.timeout = timeout
        self.live = live

        # preset argument will be overident by discussion
        if discussion:
            self.discussion = discussion
        else:
            self.load_preset(preset)

    def reply(self, message: str | list = None, keep_reply=None) -> str:
        # additional message will not be remembered in the meeseeks memory
        discussion = self.discussion.copy()
        if isinstance(message, dict):
            discussion.append(message)
        elif isinstance(message, list):
            discussion.extend(message)

        # If not specified, reply is not kept when a additional message is
        # passed
        if keep_reply is None:
            keep_reply = not message

        # sends the rely request using the openai package
        openai.api_key = self.api_key

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=discussion,
            temperature=self.temp,
            max_tokens=self.length,
            stream=True,  # This allows live mode and is slightly faster
        )

        content_assistant = ""  # the return message

        if self.live and keep_reply:
            init_print()  # sets text width and rests last_line_num
        # loops over the stream in real time as the chunks comme in
        for chunk in response:
            # extract the message
            chunk_content = chunk["choices"][0]["delta"].get("content", "")
            content_assistant += chunk_content
            if self.live and keep_reply:
                print_stream(content_assistant)  # Print content as it comes

        if keep_reply:
            message = {"role": "assistant", "content": content_assistant}
            self.discussion.append(message)

        return content_assistant


class llama(Meeseeks):
    pass
