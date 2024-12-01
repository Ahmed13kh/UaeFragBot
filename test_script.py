import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="ft:gpt-4o-mini-2024-07-18:personal::AZGpXZ6g",
    messages=[
        {"role": "system", "content": "You are a perfume chatbot specialized in UAE perfumes only. You provide factual and accurate responses with a touch of charm."},
        {"role": "user", "content": "What are some popular unisex perfumes?"}
    ]
)

print(response['choices'][0]['message']['content'])
