import openai

openai.api_key = "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"
job_id = "ftjob-xX0bU01T60H4yKyNHYjLzgRT"
response = openai.FineTuningJob.retrieve(id=job_id)
print(response)
