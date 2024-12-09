from flask import Flask, render_template, request
import openai
import time
app = Flask(__name__)

openai.api_key = "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"  # Replace with your OpenAI API key

# Store conversation history in memory (for this example)
conversation_history = []


@app.route('/')
def home():
    return render_template('index.html', conversation=conversation_history)


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']

    try:
        # Simulate processing time

        response = openai.ChatCompletion.create(
            model="ft:gpt-4o-mini-2024-07-18:personal::AZGpXZ6g",
            messages=[
                {"role": "system", "content": "You are a perfume chatbot specialized in UAE perfumes only. You provide factual and accurate responses with a touch of charm."},
                *[
                    {"role": "user", "content": entry['user']}
                    for entry in conversation_history
                ],
                {"role": "user", "content": user_input}
            ],
            max_tokens=300
        )
        chatbot_response = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        chatbot_response = f"Error: {str(e)}"

    # Update the conversation history
    conversation_history.append({"user": user_input, "response": chatbot_response})

    return render_template('index.html', conversation=conversation_history)


if __name__ == '__main__':
    app.run(debug=True)
