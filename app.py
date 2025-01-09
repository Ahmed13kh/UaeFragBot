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
    if isinstance(attribute, str):
        attribute = attribute.lower()  # Convert to lowercase
        attribute = re.sub(r'[-_]', ' ', attribute)  # Replace hyphens and underscores with spaces
        attribute = re.sub(r'[^\w\s]', '', attribute)  # Remove all non-alphanumeric characters except spaces
        attribute = re.sub(r'\s+', ' ', attribute)  # Collapse multiple spaces into one
        return attribute.strip()  # Remove leading and trailing spaces
    return attribute  # Return non-string attributes as-is

# Normalize perfume data
for perfume in perfume_data:
    perfume['name'] = normalize_attribute(perfume.get('name', ''))
    perfume['designer'] = normalize_attribute(perfume.get('designer', 'unknown'))
    perfume['longevity'] = normalize_attribute(perfume.get('longevity', 'unknown'))
    perfume['sillage'] = normalize_attribute(perfume.get('sillage', 'unknown'))
    perfume['pricevalue'] = normalize_attribute(perfume.get('pricevalue', 'unknown'))
    perfume['description'] = normalize_attribute(perfume.get('description', ''))
    perfume['rating'] = perfume.get('rating', 0)  # Keep numeric values as-is
    perfume['gender'] = normalize_attribute(perfume.get('gender', 'unknown'))
    perfume['season'] = normalize_attribute(perfume.get('season', 'unknown'))

# Extract preferences with flexible matching
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

    # Match rating-related intent with flexible synonyms
    rating_synonyms = {"highly rated", "top rated", "best rated", "best", "good rating", "high rating"}
    # Normalize rating synonyms for flexibility
    normalized_synonyms = {normalize_attribute(synonym) for synonym in rating_synonyms}

    # Check for matches in user input
    if any(synonym in user_input for synonym in normalized_synonyms):
        preferences["rating"] = 4.0  # Threshold for "highly rated"

    return preferences


def find_perfume_by_name(user_input):
    # Allow alphanumeric characters, spaces, and specific punctuations (e.g., | and numbers)
    cleaned_input = normalize_attribute(re.sub(r"[^\w\s|]", "", user_input))

    for perfume in perfume_data:
        perfume_name = normalize_attribute(perfume['name'])
        designer_name = normalize_attribute(perfume['designer'])

        # Case 1: Match exact name and designer
        if cleaned_input == f"{perfume_name} {designer_name}" or cleaned_input == f"{designer_name} {perfume_name}":
            return format_perfume_response(perfume)

        # Case 2: Match exact name only
        if cleaned_input == perfume_name:
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
def homepage():
    # Render the home.html as the starting page
    return render_template('home.html')
@app.route('/chatbot')
def chatbot():
    # Render the index.html for the chatbot functionality
    return render_template('index.html', perfume_data=perfume_data, fragrance_notes=fragrance_notes)


@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        # Get the selected preferences from the form
        designer = request.form.get('designer', '').lower()
        gender = request.form.get('gender', '').lower()
        season = request.form.get('season', '').lower()

        # Filter perfumes based on the selected options
        filtered_perfumes = [
            perfume for perfume in perfume_data
            if (designer == perfume['designer'].lower() or not designer) and
               (gender == perfume['gender'].lower() or not gender) and
               (season == perfume['season'].lower() or not season)
        ]

        # Pass the filtered results to the template
        return render_template('recommend.html', perfumes=filtered_perfumes)

    # For GET request, just load the form
    return render_template('recommend.html', perfumes=None)


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
if __name__ == '__main__':
    app.run(debug=True)