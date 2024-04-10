import ollama

response = ollama.generate(model='gemma:2b',
                          prompt='what is a qubit?')
print(response['response'])


