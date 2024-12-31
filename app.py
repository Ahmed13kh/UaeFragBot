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
    perfume['designer'] = normalize_attribute(perfume.get('designer', 'unknown'))
    perfume['longevity'] = normalize_attribute(perfume.get('longevity', 'unknown'))
    perfume['sillage'] = normalize_attribute(perfume.get('sillage', 'unknown'))
    perfume['pricevalue'] = normalize_attribute(perfume.get('pricevalue', 'unknown'))
    perfume['description'] = perfume.get('description', '').lower()
    perfume['rating'] = perfume.get('rating', 0)
    perfume['gender'] = normalize_attribute(perfume.get('gender', 'unknown'))

# Updated function for handling designer names dynamically
def extract_preferences(user_input):
    preferences = {}

    # Normalize user input
    user_input = normalize_attribute(user_input)

    # Match fragrance notes or description
    for note in fragrance_notes:
        if note in user_input:
            preferences["notes"] = note
            break

        # Match designer names dynamically with partial matching
    designers = {normalize_attribute(perfume['designer']) for perfume in perfume_data}
    for designer in designers:
        if designer in user_input or any(word in user_input for word in designer.split()):
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
# Improved function to find perfumes by name
def find_perfume_by_name(user_input):
    cleaned_input = normalize_attribute(re.sub(r"[^\w\s]", "", user_input))

    # Attempt exact match with normalized names
    for perfume in perfume_data:
        if cleaned_input in perfume['name'] or cleaned_input in f"{perfume['name']} by {perfume['designer']}":
            return format_perfume_response(perfume)

    # Attempt partial match for designer and perfume names
    for perfume in perfume_data:
        if cleaned_input in normalize_attribute(perfume['name']) or cleaned_input in normalize_attribute(perfume['designer']):
            return format_perfume_response(perfume)

    return None

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
            elif key == "designer":
                    # Allow partial matches for designer names
                designer_name = normalize_attribute(perfume.get("designer", ""))
                if value_lower not in designer_name and not any(
                    word in designer_name for word in value_lower.split()):
                    match = False
                    break
            else:
                # Match other attributes (exact match)
                if normalize_attribute(perfume.get(key, '')) != value_lower:
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

        # Check for specific perfume queries with flexible intent extraction
        intent_match = re.search(
            r"(tell me about|describe|what can you say about|give me details about|talk about)\s+(.*)", user_input,
            re.IGNORECASE)
        if intent_match:
            perfume_name = intent_match.group(2).strip()
            perfume_details = find_perfume_by_name(perfume_name)
            if perfume_details:
                return jsonify({"structured": perfume_details})
            else:
                # Fallback to fine-tuned GPT for general response
                response = fallback_general_response(user_input)
                return jsonify({"response": response})

        # Extract preferences
        criteria = extract_preferences(user_input)

        # Recommend based on criteria
        if criteria:
            recommendations = recommend_perfumes_by_criteria(criteria)
            if recommendations:
                return jsonify({"structured": recommendations})
            else:
                # Fallback to fine-tuned GPT for general response
                response = fallback_general_response(user_input)
                return jsonify({"response": response})

        # Fallback: Use fine-tuned GPT for general queries
        response = fallback_general_response(user_input)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Helper function for GPT fallback
def fallback_general_response(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="ft:gpt-4o-2024-08-06:personal::AjoMgZCP",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and friendly perfume consultant specializing in UAE perfumes only."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "I'm sorry, but I couldn't process your request right now. Please try again later."
