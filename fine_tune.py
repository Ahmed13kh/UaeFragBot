import openai

openai.api_key = "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"

response = openai.FineTuningJob.create(
    training_file="file-AFKRtmMTDiEaWjnvMGaA3p",
    model="gpt-4o-2024-08-06"
)
print(response)
