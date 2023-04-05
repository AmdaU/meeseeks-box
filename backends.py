import os
import requests
import json
import subprocess
import datetime
import functools
import openai

script_dir = os.path.dirname(os.path.realpath(__file__))


class Meeseeks:
    def __init__(self):
        self.archive = {}
        self.archive_file = None

    def reply(self, message: str):
        """
        This method is the most important for a meeseeks as it it the one
        who actaly request a reply from the llm this method however
        oviously depends on the specif backends and needs to be reimplemented
        every time, this is just a placeholder
        """
        print(self.__class__.__name__, "backend was not implemented yet")

    def tell(self, message: str, role: str = 'user'):
        message_user = {"role": role, "content": message}
        self.discussion.append(message_user)

    def save_discussion(self):
        self.archive['discussion'] = self.discussion
        if not self.archive_file:
            self.archive['title'] = self.title
            self.archive_file = f'{script_dir}/archive/{str(datetime.datetime.now()).replace(" ","")}'
        with open(self.archive_file, 'w+') as file:
            json.dump(self.archive, file)

    def create_new_Meeseeks(self):
        pass

    def load_preset(self, preset):
        '''Sets up the "preset", aka info before the discussion starts'''
        presets = {}
        with open(f'{script_dir}/gpt_presets.json') as read:
            presets = json.load(read)
        preset_list = list(presets)

        if preset not in preset_list:
            print("This preset does not exist, using default")
            preset = 'default'
        self.discussion = presets[preset]['prompt']

        # Some presets will pull 'live' data from the system of elsewhere
        if 'data' in presets[preset]:
            for data_name, data_command in presets[preset]['data'].items():
                result = subprocess.run([data_command],
                                        shell=True,
                                        capture_output=True).stdout.decode()
                self.discussion[0]["content"] = self.discussion[0]["content"]\
                    .replace('{' + str(data_name) + '}', result)

    def remember(self, specific=None):
        if not specific:
            specific="the current whole conversation"

        message = {'role':'system', 'content': f'You shall now try to summerise something that was mentioned in this conversation. Make it concise but clear. It will later be used to remind you of what happend in the conversation. Use key points if you have to. The information does **not** need to be clear to a human, **only** to you. The subject of your note is: {specific}'}
        note = self.reply(message)
        print(note)

    @property
    @functools.lru_cache() # Once generated, the title stays
    def title(self):
        """gives a title to the current discussion"""
        # temporarily sets it's temperature to 0 for les "messy" result
        old_temp = self.temp
        self.temp = 0
        message = {'role':'system', 'content': 'give a short title to this conversation. Do not provide'
                ' **any** explanation or aditional content. Do not give **any** formating like "Title:" or similar. Do not end with a dot.'}
        title = self.reply(message)

        self.temp = old_temp # resets the temperature
        return title


# gpt 3.5 backend -------------------------------------------------------------
class gpt35(Meeseeks):

    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str = '', max_number_of_tries: int = 3,
                 temp: int = 1, length=100, timeout=10, preset='default',
                 discussion=None):
        super(gpt35, self).__init__()
        if api_key == '':
            with open(f"{script_dir}/open_ai.secrets") as secret:
                self.api_key = secret.readline().strip('\n')
        else:
            self.api_key = api_key

        self.max_number_of_tries = max_number_of_tries
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.temp = temp
        self.length = length
        self.timeout = timeout

        # preset argument will be overident by discussion
        if discussion:
            self.discussion = discussion
        else:
            self.load_preset(preset)

    def reply(self, message=None) -> str:
        openai.api_key = self.api_key
        discussion = self.discussion

        if message:
            discussion.append(message)
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=self.discussion,
            temperature=self.temp,
            max_tokens=self.length,
            stream=True  # again, we set stream=True
        )
        collected_messages = []
        for chunk in response:
            chunk_message = chunk['choices'][0]['delta']  # extract the message
            collected_messages.append(chunk_message)
        content_assistant = ''.join([m.get('content', '') for m in collected_messages])

        message = {"role": "assistant", "content": content_assistant}
        self.discussion.append(message)

        return content_assistant


class llama(Meeseeks):
    pass
