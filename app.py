from flask import Flask, render_template, request, jsonify
import openai
import json
from fragrance_notes import fragrance_notes

app = Flask(__name__)
openai.api_key = "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"

# Load perfume data
with open("perfume_data.json", "r") as file:
    perfume_data = json.load(file)

def find_perfume_by_name(name):
    """Search for a specific perfume by name and return comprehensive details."""
    for perfume in perfume_data:
        if name.lower() in perfume['name'].lower():
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
    return {"error": "Perfume not found"}

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
    return recommendations[:3] if recommendations else [{"error": f"No perfumes found for the note '{note}'"}]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.form['user_input'].strip().lower()

        # Handle specific perfume queries
        if "tell me about" in user_input:
            perfume_name = user_input.split("about")[-1].strip()
            perfume_details = find_perfume_by_name(perfume_name)
            return jsonify({"structured": perfume_details}) if perfume_details else jsonify({"error": "Perfume not found"})

        # Handle fragrance type recommendations

        for note in fragrance_notes:
            if note in user_input.lower():
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
