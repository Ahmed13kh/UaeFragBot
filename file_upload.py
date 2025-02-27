import openai

openai.api_key = "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"
response = openai.File.create(
    file=open("fine_tuning_data.jsonl", "rb"),
    purpose="fine-tune"
)

# Print file ID
print("File uploaded successfully. File ID:", response["id"])
