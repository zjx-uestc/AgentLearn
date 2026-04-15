import ollama


response = ollama.chat(model='deepseek-r1:8b', stream=False, messages=[
  {
    'role': 'user',
    'content': '你是在本地运行吗？',
  },
])

print(response['message']['content'])