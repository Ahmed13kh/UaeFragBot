import openai

openai.api_key = "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"
response = openai.FineTuningJob.create(
    training_file="file-AFKRtmMTDiEaWjnvMGaA3p",
    model="gpt-4o-2024-08-06"
)
print(response)
