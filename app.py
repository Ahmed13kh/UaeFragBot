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
    perfume['season'] = normalize_attribute(perfume.get('season', 'unknown'))


# Updated function for handling designer names dynamically
def extract_preferences(user_input):
    preferences = {}

    # Normalize user input
    user_input = normalize_attribute(user_input)

    # Match fragrance notes in the description
    for note in fragrance_notes:
        if note in user_input:
            preferences["description_match"] = note
            break

    # Match notes in perfume data
    notes_attributes = ['top notes', 'mid notes', 'base notes']
    for perfume in perfume_data:
        for attr in notes_attributes:
            if any(note in user_input for note in perfume.get(attr, [])):
                preferences["notes_match"] = perfume['name']
                break

    # Match attributes: longevity, sillage, pricevalue, gender
    attributes = {
        "longevity": {perfume['longevity'] for perfume in perfume_data},
        "sillage": {perfume['sillage'] for perfume in perfume_data},
        "pricevalue": {perfume['pricevalue'] for perfume in perfume_data},
        "gender": {perfume['gender'] for perfume in perfume_data},
        "designer": {perfume['designer'] for perfume in perfume_data},
        "season": {perfume['season'] for perfume in perfume_data}

    }

    for attr, values in attributes.items():
        for value in values:
            if value in user_input:
                preferences[attr] = value
                break

    # Match rating-related intent
    rating_synonyms = {"highly rated", "top rated", "best rated", "best", "good rating", "high rating"}
    if any(synonym in user_input for synonym in rating_synonyms):
        preferences["rating"] = 4.0  # Threshold for "highly rated"

    return preferences


def find_perfume_by_name(user_input):
    cleaned_input = normalize_attribute(re.sub(r"[^\w\s']", "", user_input))

    for perfume in perfume_data:
        perfume_name = normalize_attribute(perfume['name'])
        designer_name = normalize_attribute(perfume['designer'])

        # Case 1: Match exact name and designer without relying on "by"
        if cleaned_input in f"{perfume_name} {designer_name}" or cleaned_input in f"{designer_name} {perfume_name}":
            return format_perfume_response(perfume)

        # Case 2: Match exact name only
        if cleaned_input == perfume_name:
            return format_perfume_response(perfume)

        # Case 3: Match designer name followed by part of the perfume name
        if cleaned_input.startswith(designer_name) and perfume_name in cleaned_input:
            return format_perfume_response(perfume)

        # Case 4: Match perfume name followed by part of the designer name
        if cleaned_input.startswith(perfume_name) and designer_name in cleaned_input:
            return format_perfume_response(perfume)

    # No matches found
    return None


def recommend_perfumes_by_criteria(criteria, num_recommendations=3):
    recommendations = []
    for perfume in perfume_data:
        match = True
        for key, value in criteria.items():
            value_lower = normalize_attribute(value)
            if key == "description_match":
                # Match description with fragrance_notes
                if value_lower not in perfume.get('description', ''):
                    match = False
                    break
            elif key == "notes_match":
                # Match notes in perfume data
                notes_attributes = ['top notes', 'mid notes', 'base notes']
                if not any(value_lower in note.lower() for attr in notes_attributes for note in perfume.get(attr, [])):
                    match = False
                    break
            elif key == "rating":
                if perfume['rating'] < value:  # Handle numeric attribute
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
        "season": perfume['season'],
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
    return render_template('index.html', perfume_data=perfume_data, fragrance_notes=fragrance_notes)


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
