import os
import requests
import json
import subprocess

script_dir = os.path.dirname(os.path.realpath(__file__))


class Meeseeks:
    def reply(self, message: str, discussion: list):
        print(self.__class__.__name__, "backend was not implemented yet")

    def create_discussion_instance(self):
        pass

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

        if 'data' in presets[preset]:
            for data_name, data_command in presets[preset]['data'].items():
                result = subprocess.run([data_command],
                                        shell=True,
                                        capture_output=True).stdout.decode()
                self.discussion[0]["content"] = self.discussion[0]["content"]\
                    .replace('{' + str(data_name) + '}', result)


# gpt 3.5 backend -------------------------------------------------------------
class gpt35(Meeseeks):

    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str = '', max_number_of_tries: int = 3,
                 temp: int = 1, length=100, timeout=10, preset='default',
                 discussion=None):
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

    def tell(self, message: str, role: str = 'user'):
        message_user = {"role": role, "content": message}
        self.discussion.append(message_user)

    def reply(self) -> str:

        # The data to send to the API
        data = {
            "model": "gpt-3.5-turbo",
            "messages": self.discussion,
            "max_tokens": self.length,
            "temperature": self.temp,
        }

        for i in range(self.max_number_of_tries):
            response = requests.post(self.endpoint,
                                     headers=self.headers,
                                     data=json.dumps(data),
                                     timeout=self.timeout)
            match response.status_code:
                case 200:
                    content_assistant =\
                        response.json()['choices'][-1]['message']['content']
                    break
                case _:
                    print(f"an oupise of type {response.status_code} happend, retrying...")
        if i == self.max_number_of_tries - 1:
            raise(Exception("was not able to contact server"))

        message = {"role": "assistant", "content": content_assistant}
        self.discussion.append(message)

        return content_assistant

class llama(Meeseeks):
    pass
