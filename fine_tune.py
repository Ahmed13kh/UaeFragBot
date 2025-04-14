import openai

openai.api_key = " "
response = openai.FineTuningJob.create(
    training_file="file-VacjgFzNoGbPgQfwJpSeoG",
    model="gpt-4o-2024-08-06"
)
print(response)
