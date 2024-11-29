import openai

openai.api_key = "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"

fine_tune_response = openai.FineTune.create(
    training_file="file-W7NZ4K4FPrtxwjNWC41qm1",  # Your file ID
    model="curie"  # Base model for fine-tuning
)
print("File uploaded successfully. File ID:", fine_tune_response["id"])
