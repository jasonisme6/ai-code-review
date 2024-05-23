import os

from openai import OpenAI

client = OpenAI(
    api_key='',
)

def start_gpt_review_code(code_list):

    # Create a single large prompt including all code blocks
    prompt = ("Give a code review each of the following code blocks and explain their functionality, "
              "please give a detail review:\n\n")
    for i, code in enumerate(code_list):
        prompt += f"### Code Block {i+1}:\n{code}\n\n"

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    answer = chat_completion.choices[0].message.content.strip()
    return answer
