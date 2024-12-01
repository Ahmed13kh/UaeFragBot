import openai

openai.api_key = "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"

result_file_id = "file-MwuogLj6rSipz1jJwjxUfZ"
result = openai.File.download(result_file_id)

with open("result_file.json", "wb") as f:
    f.write(result)
print("Result file downloaded!")
