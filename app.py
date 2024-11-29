from flask import Flask, render_template, request
import openai

# Initialize Flask app
app = Flask(__name__)

# Your OpenAI API key
openai.api_key = "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"  # Replace with your API key

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Chatbot response route
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    # Call OpenAI API for generating a response
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=f"You are a perfume chatbot specialized in UAE perfumes only. You provide factual and accurate responses with a touch of charm. Answer based on the following: {user_input}",
        max_tokens=300
    )
    chatbot_response = response.choices[0].text.strip()
    return render_template('index.html', user_input=user_input, chatbot_response=chatbot_response)

if __name__ == '__main__':
    app.run(debug=True)
