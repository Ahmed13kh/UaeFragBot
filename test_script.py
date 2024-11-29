import openai

# Set your OpenAI API key
openai.api_key = "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"

# Define a test prompt
test_prompt = "What are some affordable Arabian perfumes for daily wear? ->"

# Send the test prompt to your fine-tuned model
response = openai.ChatCompletion.create(
    model="ft:gpt-4o-mini-2024-07-18",  # Replace with your fine-tuned model's ID
    messages=[
        {"role": "system", "content": "You are a perfume chatbot specialized in UAE perfumes only. You provide factual and accurate responses with a touch of charm."},
        {"role": "user", "content": test_prompt}
    ],
    max_tokens=300,  # Limit the number of tokens in the response
    temperature=0.5  # Adjust temperature for response creativity
)

# Print the model's response
print("Prompt:", test_prompt)
print("Completion:", response['choices'][0]['message']['content'])
