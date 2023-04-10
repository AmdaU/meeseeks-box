import os
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
        who actually request a reply from the llm this method however
        obviously depends on the specif backends and needs to be reimplemented
        every time, this is just a placeholder
        """
        print(self.__class__.__name__, "backend was not implemented yet")

    def tell(self, message: str, role: str = 'user'):
        """adds a message to the meeseeks mid-term memory"""
        message_user = {"role": role, "content": message}
        self.discussion.append(message_user)

    def save_discussion(self):
        """saves the current discussion along with other info to a file"""
        self.archive['discussion'] = self.discussion
        if not self.archive_file:
            # the filename is simply the current time, which isn't a great name
            self.archive['title'] = self.title
            filename = str(datetime.datetime.now()).replace(" ", "_")
            self.archive_file = f'{script_dir}/archive/{filename}'
        with open(self.archive_file, 'w+') as file:
            json.dump(self.archive, file)

    def create_new_Meeseeks(self):
        pass

    def load_preset(self, preset_name):
        '''Sets up the "preset", aka info before the discussion starts'''
        #Loading the preset info from the json file
        presets = {}
        with open(f'{script_dir}/gpt_presets.json') as read:
            presets = json.load(read)
        preset_list = list(presets)

        if preset_name not in preset_list:
            print("This preset does not exist, using default")
            preset_name = 'default'

        preset = presets[preset_name]

        self.discussion = preset['prompt']

        # Some presets will pull 'live' data from the system of elsewhere
        if 'data' in preset:
            for data_name, data_command in preset['data'].items():
                result = subprocess.run([data_command],
                                        shell=True,
                                        capture_output=True).stdout.decode()
                self.discussion[0]["content"] = self.discussion[0]["content"]\
                    .replace('{' + str(data_name) + '}', result)

    def remember(self, specific=None):
        """store information the the long term memory"""
        if not specific:
            specific = "the current whole conversation"

        message = {'role':'system',
                   'content': f'You shall now try to summerise something that'
                   'was mentioned in this conversation. Make it concise but'
                   'clear. It will later be used to remind you of what happend'
                   'in the conversation. Use key points if you have to. The'
                   'information does **not** need to be clear to a human,'
                   '**only** to you. The subject of your note is: {specific}'}
        note = self.reply(message)
        print(note)

    @property
    @functools.lru_cache() # Once generated, the title stays
    def title(self):
        """gives a title to the current discussion"""
        # temporarily sets it's temperature to 0 for les "messy" result
        old_temp = self.temp
        self.temp = 0
        message = {'role':'system',
                   'content': 'give a short title to this conversation.'
                   'Do not provide **any** explanation or aditional content.'
                   'Do not give **any** formating like "Title:" or similar.'
                   'Do not end with a dot.'}
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

    def reply(self, message: str = None, live: bool=False) -> str:

        # additional message will not be remembered in the meeseeks memory
        discussion = self.discussion
        if message:
            discussion.append(message)

        openai.api_key = self.api_key

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=self.discussion,
            temperature=self.temp,
            max_tokens=self.length,
            stream=True  # again, we set stream=True
        )

        content_assistant = ""
        out_stty = subprocess.run(["stty size"], shell=True, capture_output=True)
        height, width = out_stty.stdout.decode().split(' ')
        height, width = int(height), int(width)
        last_lines_num =0
        for chunk in response:
            chunk_message = chunk['choices'][0]['delta']  # extract the message
            chunk_content = chunk_message.get('content','')
            content_assistant += chunk_content
            if live:
                out = subprocess.run([f"glow -s '{script_dir}/ressources/gpt_style.json' -w {width}"], shell=True, input=(content_assistant).encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out_string = out.stdout.decode('utf-8')
                lines = out_string.split('\n')
                lines_out = subprocess.run(["wc -l"], shell=True, input = out.stdout, capture_output=True)
                lines_num = len(lines)

                amount_to_print = min(height-3, lines_num)
                number_of_new_line = lines_num-last_lines_num
                amount_to_erase = amount_to_print - (number_of_new_line)
                print(f'\033[{amount_to_erase}A', end='\r')
                for line in lines[-amount_to_print:]:
                    print(line)
                last_lines_num = lines_num

        message = {"role": "assistant", "content": content_assistant}
        self.discussion.append(message)

        return content_assistant


class llama(Meeseeks):
    pass
