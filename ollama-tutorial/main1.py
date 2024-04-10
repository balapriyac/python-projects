from langchain_community.llms import Ollama

llm = Ollama(model="llama2")

llm.invoke("tell me about partial functions in python")
