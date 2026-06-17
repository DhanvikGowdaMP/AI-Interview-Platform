import ollama

response = ollama.chat(
    model='llama3',
    messages=[
        {
            'role': 'user',
            'content': 'Generate 5 Python interview questions'
        }
    ]
)

print(response['message']['content'])