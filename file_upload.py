import openai

openai.api_key = " "
response = openai.File.create(
    file=open("fine_tuning_data.jsonl", "rb"),
    purpose="fine-tune"
)
print("File uploaded successfully. File ID:", response["id"])
