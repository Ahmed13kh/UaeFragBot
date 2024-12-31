from flask import Flask, render_template, request, jsonify
import openai
import json
import random
import re
from fragrance_notes import fragrance_notes

app = Flask(__name__)
openai.api_key = "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"

# Load perfume data
with open("perfume_data.json", "r") as file:
    perfume_data = json.load(file)

# Normalize attributes for consistent matching
def normalize_attribute(attribute):
    return attribute.lower().strip() if isinstance(attribute, str) else attribute

# Normalize perfume data
for perfume in perfume_data:
    perfume['name'] = normalize_attribute(perfume.get('name', ''))
    perfume['designer'] = normalize_attribute(perfume.get('designer', ''))
    perfume['longevity'] = normalize_attribute(perfume.get('longevity', 'unknown'))
    perfume['sillage'] = normalize_attribute(perfume.get('sillage', 'unknown'))
    perfume['pricevalue'] = normalize_attribute(perfume.get('pricevalue', 'unknown'))
    perfume['description'] = perfume.get('description', '').lower()
    perfume['rating'] = perfume.get('rating', 0)
    perfume['gender'] = normalize_attribute(perfume.get('gender', 'unknown'))

# Extract preferences from user input
def extract_preferences(user_input):
    preferences = {}

    # Match fragrance notes or description
    for note in fragrance_notes:
        if note in user_input:
            preferences["notes"] = note
            break

    # Match designer names dynamically
    designers = {normalize_attribute(perfume['designer']) for perfume in perfume_data}
    for designer in designers:
        if designer in user_input:
            preferences["designer"] = designer
            break

    # Match attributes: longevity, sillage, pricevalue, gender
    attributes = {
        "longevity": {perfume['longevity'] for perfume in perfume_data},
        "sillage": {perfume['sillage'] for perfume in perfume_data},
        "pricevalue": {perfume['pricevalue'] for perfume in perfume_data},
        "gender": {perfume['gender'] for perfume in perfume_data}
    }

    for attr, values in attributes.items():
        for value in values:
            if value in user_input:
                preferences[attr] = value
                break

    # Match rating-related intent
    rating_synonyms = {"highly rated", "top rated", "best rated", "good rating", "high rating"}
    if any(synonym in user_input for synonym in rating_synonyms):
        preferences["rating"] = 4.0  # Threshold for "highly rated"

    return preferences

# Find perfumes by name
def find_perfume_by_name(user_input):
    cleaned_input = normalize_attribute(re.sub(r"[^\w\s]", "", user_input))
    for perfume in perfume_data:
        if cleaned_input in perfume['name'] or cleaned_input in f"{perfume['name']} by {perfume['designer']}":
            return format_perfume_response(perfume)
    return None

# Recommend perfumes by criteria
def recommend_perfumes_by_criteria(criteria, num_recommendations=3):
    recommendations = []
    for perfume in perfume_data:
        match = True
        for key, value in criteria.items():
            value_lower = normalize_attribute(value)
            if key == "notes":
                # Match notes or description
                if not any(value_lower in note.lower() for note in perfume.get('top notes', []) + perfume.get('mid notes', []) + perfume.get('base notes', [])) \
                        and value_lower not in perfume.get('description', ''):
                    match = False
                    break
            elif key == "rating":
                if perfume['rating'] < value:  # Handle numeric attribute
                    match = False
                    break
            elif normalize_attribute(perfume.get(key, '')) != value_lower:
                match = False
                break
        if match:
            recommendations.append(format_perfume_response(perfume))

    random.shuffle(recommendations)
    return recommendations[:num_recommendations]

# Format perfume response
def format_perfume_response(perfume):
    return {
        "name": perfume['name'].title(),
        "designer": perfume['designer'].title(),
        "gender": perfume['gender'],
        "rating": f"{perfume['rating']}/5",
        "description": perfume['description'],
        "top_notes": ', '.join(perfume.get('top notes', [])),
        "mid_notes": ', '.join(perfume.get('mid notes', [])),
        "base_notes": ', '.join(perfume.get('base notes', [])),
        "longevity": perfume['longevity'],
        "sillage": perfume['sillage'],
        "pricevalue": perfume['pricevalue'],
        "link": perfume.get('url', ''),
        "image": perfume.get('image', '')
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.form['user_input'].lower()

        # Check for specific perfume queries
        if "tell me about" in user_input or "describe" in user_input:
            perfume_name = re.sub(r"(tell me about|describe)", "", user_input, flags=re.IGNORECASE).strip()
            perfume_details = find_perfume_by_name(perfume_name)
            return jsonify({"structured": perfume_details}) if perfume_details else jsonify({"error": "Perfume not found."})

        # Extract preferences
        criteria = extract_preferences(user_input)

        # Recommend based on criteria
        if criteria:
            recommendations = recommend_perfumes_by_criteria(criteria)
            return jsonify({"structured": recommendations}) if recommendations else jsonify({"error": "No perfumes found matching your preferences."})

        # Fallback: Use fine-tuned GPT for general queries
        response = openai.ChatCompletion.create(
            model="ft:gpt-4o-2024-08-06:personal::AjoMgZCP",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and friendly perfume consultant specializing in UAE perfumes Only"},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500
        )
        gpt_response = response['choices'][0]['message']['content'].strip()
        return jsonify({"response": gpt_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
