import openai

openai.api_key = "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"

response = openai.FineTuningJob.create(
    training_file="file-AFKRtmMTDiEaWjnvMGaA3p",
    model="gpt-4o-2024-08-06"
)
print(response)
