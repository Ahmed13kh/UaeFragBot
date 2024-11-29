import openai

openai.api_key = "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"

response = openai.FineTuningJob.create(
    training_file="file-W7NZ4K4FPrtxwjNWC41qm1",
    model="gpt-4o-mini-2024-07-18"
)
print(response)
