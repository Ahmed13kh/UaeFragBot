import openai

openai.api_key = "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"  # Replace with your API key

files = openai.File.list()
print(files)
