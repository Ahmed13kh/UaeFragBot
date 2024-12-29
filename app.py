from flask import Flask, render_template, request, jsonify
import openai
import json
from fragrance_notes import fragrance_notes

app = Flask(__name__)
openai.api_key = "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"

# Load perfume data
with open("perfume_data.json", "r") as file:
    perfume_data = json.load(file)

import re

def find_perfume_by_name(user_input):
    """Search for a specific perfume by name and return comprehensive details."""
    # Normalize the input
    cleaned_input = re.sub(r"[^\w\s]", "", user_input.lower().strip())  # Remove punctuation

    # Iterate through perfumes and check for matches
    for perfume in perfume_data:
        perfume_name = perfume['name'].lower()
        designer_name = perfume['designer'].lower()

        # Match the perfume name or 'name by designer'
        if cleaned_input in perfume_name or cleaned_input in f"{perfume_name} by {designer_name}":
            return {
                "name": perfume['name'],
                "designer": perfume['designer'],
                "gender": perfume['gender'],
                "rating": f"{perfume['rating']}/5",
                "description": perfume['description'],
                "top_notes": ', '.join(perfume.get('top notes', [])),
                "mid_notes": ', '.join(perfume.get('mid notes', [])),
                "base_notes": ', '.join(perfume.get('base notes', [])),
                "longevity": perfume.get('longevity', 'Unknown'),
                "sillage": perfume.get('sillage', 'Unknown'),
                "pricevalue": perfume.get('pricevalue', 'Unknown'),
                "link": perfume['url'],
                "image": perfume['image']
            }

    # No match found
    return {"error": f"Perfume '{user_input}' not found. Please try another name or variation."}


def recommend_perfumes_by_type(note):
    """Recommend perfumes based on a specified fragrance note."""
    recommendations = [
        {
            "name": perfume['name'],
            "designer": perfume['designer'],
            "rating": f"{perfume['rating']}/5",
            "description": perfume['description'],
            "top_notes": ', '.join(perfume.get('top notes', [])),
            "mid_notes": ', '.join(perfume.get('mid notes', [])),
            "base_notes": ', '.join(perfume.get('base notes', [])),
            "longevity": perfume.get('longevity', 'Unknown'),
            "sillage": perfume.get('sillage', 'Unknown'),
            "pricevalue": perfume.get('pricevalue', 'Unknown'),
            "link": perfume['url'],
            "image": perfume['image']
        }
        for perfume in perfume_data if note.lower() in ', '.join(perfume.get('top notes', []) + perfume.get('mid notes', []) + perfume.get('base notes', [])).lower()
    ]
    return recommendations[:3] if recommendations else None

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.form['user_input'].strip().lower()

        # Handle specific perfume queries
        if "tell me about" in user_input or "describe" in user_input or "can you describe" in user_input:
            # Extract the perfume name
            perfume_name = re.sub(r"(tell me about|describe|can you describe)", "", user_input, flags=re.IGNORECASE).strip()
            perfume_details = find_perfume_by_name(perfume_name)
            if "error" in perfume_details:
                return jsonify({"error": perfume_details["error"]})
            return jsonify({"structured": perfume_details})

        # Handle fragrance type recommendations
        for note in fragrance_notes:
            if note in user_input:
                recommendations = recommend_perfumes_by_type(note)
                if recommendations:
                    return jsonify({"structured": recommendations})
                else:
                    return jsonify({"error": f"No perfumes found for the note '{note}'"})

        # Use GPT-4 for general queries
        response = openai.ChatCompletion.create(
            model="ft:gpt-4o-2024-08-06:personal::AjoMgZCP",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and friendly perfume consultant specializing in UAE perfumes only."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500
        )
        gpt_response = response['choices'][0]['message']['content'].strip()
        return jsonify({"response": gpt_response})

    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
