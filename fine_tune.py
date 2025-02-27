import openai

<<<<<<< HEAD
openai.api_key = "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"
=======
openai.api_key = "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"
>>>>>>> d31ba4e62092807203a57694d44ce1727f92db67

response = openai.FineTuningJob.create(
    training_file="file-AFKRtmMTDiEaWjnvMGaA3p",
    model="gpt-4o-2024-08-06"
)
print(response)
