import openai

openai.api_key = "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"

response = openai.File.create(
    file=open("fine_tuning_data.jsonl", "rb"),
    purpose="fine-tune"
)

# Print file ID
print("File uploaded successfully. File ID:", response["id"])
