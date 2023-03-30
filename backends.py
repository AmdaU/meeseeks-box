import os
import requests
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))

class Meeseeks:
    def send_request(self, message, discussion):
        print(self.__class__.__name__, "backend was not implemented yet")

    def create_discussion_instance(self):
        pass

    def create_new_Meeseeks(self):
        pass

# gpt 3.5 backend -------------------------------------------------------------

class gpt35(Meeseeks):

    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str = '', max_number_of_tries: int = 3, ):
        if api_key == '':
            with open(f"{script_dir}/open_ai.secrets") as secret:
                self.api_key = secret.readline().strip('\n')
        else:
            self.api_key = api_key
        self.max_number_of_tries = max_number_of_tries
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def send_request(self, message, discussion):

        message_user = {"role": "user", "content": content_user}

        discussion.append(message_user)

        # The data to send to the API
        data = {
            "model": "gpt-3.5-turbo",
            "messages": discussion,
            "max_tokens": args.response_length,
            "temperature": args.temperature,
        }

        content_assistant = send_request(data, headers, args.backend)

        message = {"role": "assistant", "content": content_assistant}
        discussion.append(message)

        with open(f'{script_dir}/log/discussion.txt', 'w') as file:
            file.write(str(discussion))

        with open('temp.txt', 'w') as file:
            file.write(content_assistant)

    def gpt35_req(data, headers, backend):
        '''Attempts to send the request to the backend'''
        for _ in range(max_number_of_tries):
            response = requests.post(endpoint,
                                    headers=headers,
                                    data=json.dumps(data),
                                    timeout=args.t)
            match response.status_code:
                case 200:
                    message = response.json()['choices'][-1]['message']['content']
                    return message
                case _:
                    print(f"an oupise of type {response.status_code} happend, retrying...")

        sys.exit(1)

class llama(Meeseeks):
    pass
