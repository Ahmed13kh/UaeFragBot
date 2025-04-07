import openai

openai.api_key = "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"
response = openai.FineTuningJob.create(
    training_file="file-AFKRtmMTDiEaWjnvMGaA3p",
    model="gpt-4o-2024-08-06"
)
print(response)
