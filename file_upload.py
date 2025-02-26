import openai

openai.api_key = "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"

response = openai.File.create(
    file=open("fine_tuning_data.jsonl", "rb"),
    purpose="fine-tune"
)

# Print file ID
print("File uploaded successfully. File ID:", response["id"])
