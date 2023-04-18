import openai

from config import open_ai_key


openai.api_key = open_ai_key
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "hi"}],
    stream=True,  # This allows live mode and is slightly faster
)


print(type(response))


def response_content():
    for chunk in response:
        yield chunk["choices"][0]["delta"].get("content", "")


content = response_content()

for i in content:
    print(i)
