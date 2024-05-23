from gpt.gpt_review_code import start_gpt_review_code

#got review code
if __name__ == "__main__":
    code_list = ["""
import requests
import json

# Your OpenAI API key
api_key = 'your_API_key'

def review_code(code_blocks):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # Create a single large prompt including all code blocks
    prompt = "Review each of the following code blocks and explain their functionality:\\n\\n"
    for i, code in enumerate(code_blocks, 1):
        prompt += f"### Code Block {i}:\\n{code}\\n\\n"

    data = {
        "model": "gpt-3.5-turbo",  # Model selection, adjust based on available models
        "prompt": prompt,
        "temperature": 0.5,
        "max_tokens": 1000
    }

    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
    if response.status_code == 200:
        # Parse the text returned by the model
        generated_text = response.json()['choices'][0]['text'].strip()
        # Split the text by "### Code Block X:" delimiter
        reviews = generated_text.split("### Code Block")[1:]  # Skip the first empty element
        # Clean and extract content for each section
        reviews = [review.split('\\n', 1)[1].strip() if '\\n' in review else review.strip() for review in reviews]
        return reviews
    else:
        return ["Error: Unable to process the code blocks"]

# Example array of code blocks
code_blocks = [
    "def add(a, b):\\n    return a + b",
    "import math\\nprint(math.sqrt(16))"
]

# Get review results
review_results = review_code(code_blocks)
print(review_results)
""", 'print("666")\n']
    answer = start_gpt_review_code(code_list)
    print(answer)
