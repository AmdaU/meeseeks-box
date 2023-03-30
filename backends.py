import os
import requests
import sys

script_dir = os.path.dirname(os.path.realpath(__file__))

class llm_backend:
    pass

# gpt 3.5 backend -------------------------------------------------------------

class gpt35(llm_backend):

    def __init__(self, max_number_of_tries: int = 3, api_key: str = ''):
        pass
    def gpt35_req(message, ):
        # Number of times a request will be attempted to
        max_number_of_tries = 3

        # gets the api key
        api_key = ''
        with open(f"{script_dir}/open_ai.secrets") as secret:
            api_key = secret.readline().strip('\n')

        # The API endpoint for the model you want to use
        endpoint = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

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

    def send_request(data, headers, backend):
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


