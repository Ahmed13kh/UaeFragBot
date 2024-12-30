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

def normalize_attribute(attribute):
    """Normalize an attribute value for consistent comparison."""
    return attribute.lower().strip() if isinstance(attribute, str) else attribute

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

# Normalize `perfume_data` attributes for reliable matching
for perfume in perfume_data:
    perfume['longevity'] = normalize_attribute(perfume.get('longevity', 'unknown'))
    perfume['sillage'] = normalize_attribute(perfume.get('sillage', 'unknown'))
    perfume['pricevalue'] = normalize_attribute(perfume.get('pricevalue', 'unknown'))
    perfume['description'] = perfume.get('description', '').lower()  # Normalize description for fragrance_notes matching
    perfume['designer'] = normalize_attribute(perfume.get('designer', 'unknown'))
    perfume['rating'] = perfume.get('rating', 0)

def recommend_perfumes_by_criteria(criteria, num_recommendations=3):
    """Recommend perfumes based on multiple criteria."""
    recommendations = []

    for perfume in perfume_data:
        match = True  # Assume the perfume matches all criteria until proven otherwise

        for key, value in criteria.items():
            value_lower = value.lower()

            if key == "notes":
                # Check in top, mid, and base notes
                if not any(value_lower in note.lower() for note in perfume.get('top notes', []) + perfume.get('mid notes', []) + perfume.get('base notes', [])):
                    match = False
                    break
            elif key == "designer":
                # Match designer
                if value_lower not in perfume['designer']:
                    match = False
                    break
            elif key == "rating":
                # Match rating threshold
                if float(perfume['rating']) < float(value):
                    match = False
                    break
            elif key == "longevity":
                # Match longevity
                if value_lower != perfume['longevity']:
                    match = False
                    break
            elif key == "sillage":
                # Match sillage
                if value_lower != perfume['sillage']:
                    match = False
                    break
            elif key == "pricevalue":
                # Match price value
                if value_lower != perfume['pricevalue']:
                    match = False
                    break
            elif key == "description":
                # Match fragrance_notes in the description
                if value_lower not in perfume['description']:
                    match = False
                    break

        if match:
            recommendations.append({
                "name": perfume['name'],
                "designer": perfume['designer'],
                "rating": f"{perfume['rating']}/5",
                "description": perfume['description'],
                "top_notes": ', '.join(perfume.get('top notes', [])),
                "mid_notes": ', '.join(perfume.get('mid notes', [])),
                "base_notes": ', '.join(perfume.get('base notes', [])),
                "longevity": perfume['longevity'],
                "sillage": perfume['sillage'],
                "pricevalue": perfume['pricevalue'],
                "link": perfume['url'],
                "image": perfume['image']
            })

    # Randomize the order and select a limited number of recommendations
    random.shuffle(recommendations)
    return recommendations[:num_recommendations] if recommendations else None

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
            perfume_name = re.sub(r"(tell me about|describe|can you describe)", "", user_input,
                                  flags=re.IGNORECASE).strip()
            perfume_details = find_perfume_by_name(perfume_name)
            if "error" in perfume_details:
                return jsonify({"error": perfume_details["error"]})
            return jsonify({"structured": perfume_details})

        # Extract preferences for recommendations
        criteria = {}

        # Match longevity, sillage, pricevalue, designer, and notes
        all_notes = set(
            note.lower()
            for perfume in perfume_data
            for note in perfume.get('top notes', []) + perfume.get('mid notes', []) + perfume.get('base notes', [])
        )
        all_designers = set(perfume['designer'] for perfume in perfume_data)
        all_attributes = {
            "longevity": set(perfume['longevity'] for perfume in perfume_data),
            "sillage": set(perfume['sillage'] for perfume in perfume_data),
            "pricevalue": set(perfume['pricevalue'] for perfume in perfume_data),
        }

        # Match fragrance notes from perfume_data
        for note in all_notes:
            if note in user_input:
                criteria["notes"] = note
                break

        # Match designer dynamically
        for designer in all_designers:
            if designer in user_input:
                criteria["designer"] = designer
                break

        # Match other attributes dynamically
        for attr, values in all_attributes.items():
            for value in values:
                if value in user_input:
                    criteria[attr] = value
                    break

        # Match description using fragrance_notes
        for note in fragrance_notes:
            if note in user_input:
                criteria["description"] = note
                break

        # Recommend perfumes based on extracted criteria
        if criteria:
            recommendations = recommend_perfumes_by_criteria(criteria)
            if recommendations:
                return jsonify({"structured": recommendations})
            else:
                return jsonify({"error": "No perfumes found matching your preferences."})

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
