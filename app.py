from flask import Flask, render_template, request, jsonify
import openai
import json
import random
import re
from fragrance_notes import fragrance_notes

app = Flask(__name__)
openai.api_key = " "

# Loading perfume dataset from JSON file
with open("perfume_data.json", "r") as file:
    perfume_data = json.load(file)

# Normalizing strings for consistent comparison
def normalize_attribute(attribute):
    if isinstance(attribute, str):
        attribute = attribute.lower()
        attribute = re.sub(r'[-_]', ' ', attribute)
        attribute = re.sub(r'[^\w\s]', '', attribute)
        attribute = re.sub(r'\s+', ' ', attribute)
        return attribute.strip()
    return attribute

# Cleaning and normalizing key attributes for each perfume
for perfume in perfume_data:
    perfume['name'] = normalize_attribute(perfume.get('name', ''))
    perfume['designer'] = normalize_attribute(perfume.get('designer', 'unknown'))
    perfume['longevity'] = normalize_attribute(perfume.get('longevity', 'unknown'))
    perfume['sillage'] = normalize_attribute(perfume.get('sillage', 'unknown'))
    perfume['description'] = normalize_attribute(perfume.get('description', ''))
    perfume['rating'] = perfume.get('rating', 0)
    perfume['gender'] = normalize_attribute(perfume.get('gender', 'unknown'))
    perfume['season'] = normalize_attribute(perfume.get('season', 'unknown'))

# Extracting preferences from user input
def extract_preferences(user_input):
    preferences = {}
    user_input = normalize_attribute(user_input)

    for note in fragrance_notes:
        if note in user_input:
            preferences["notes_match"] = note
            break

    # Checking if input matches notes from perfume dataset
    notes_attributes = ['top notes', 'mid notes', 'base notes']
    for perfume in perfume_data:
        for attr in notes_attributes:
            if any(note in user_input for note in perfume.get(attr, [])):
                preferences["notes_match"] = perfume['name']
                break

    # Checking for other attributes like longevity, season, etc.
    attributes = {
        "longevity": {perfume['longevity'] for perfume in perfume_data},
        "sillage": {perfume['sillage'] for perfume in perfume_data},
        "gender": {perfume['gender'] for perfume in perfume_data},
        "designer": {perfume['designer'] for perfume in perfume_data},
        "season": {perfume['season'] for perfume in perfume_data}
    }

    for attr, values in attributes.items():
        for value in values:
            if value in user_input:
                preferences[attr] = value
                break

    rating_synonyms = {"highly rated", "top rated", "best rated", "best", "good rating", "high rating"}
    normalized_synonyms = {normalize_attribute(synonym) for synonym in rating_synonyms}
    if any(synonym in user_input for synonym in normalized_synonyms):
        preferences["rating"] = 4.0
    return preferences

# Matching perfume by name
def find_perfume_by_name(user_input):
    cleaned_input = normalize_attribute(re.sub(r"[^\w\s|]", "", user_input)).strip()

    for perfume in perfume_data:
        perfume_name = normalize_attribute(perfume['name']).strip()

        if cleaned_input == perfume_name:
            return format_perfume_response(perfume)

    return None

# Filtering perfumes based on extracted preferences
def recommend_perfumes_by_criteria(criteria, num_recommendations=3):
    recommendations = []
    for perfume in perfume_data:
        match = True
        for key, value in criteria.items():
            value_lower = normalize_attribute(value)
            if key == "notes_match":
                notes_attributes = ['top notes', 'mid notes', 'base notes']
                if not any(value_lower in note.lower() for attr in notes_attributes for note in perfume.get(attr, [])):
                    match = False
                    break
            elif key == "rating":
                if perfume['rating'] < value:
                    match = False
                    break
            else:
                if normalize_attribute(perfume.get(key, '')) != value_lower:
                    match = False
                    break
        if match:
            recommendations.append(format_perfume_response(perfume))
    random.shuffle(recommendations)
    return recommendations[:num_recommendations]

# Formating perfume info for display
def format_perfume_response(perfume):
    def format_text(text):
        if not text:
            return ""
        text = text.strip()
        text = text[0].upper() + text[1:]
        if not text.endswith('.'):
            text += '.'
        return text

    def format_notes(notes):
        formatted = ', '.join(note.strip().capitalize() for note in notes if note.strip())
        return formatted + '.' if formatted else ""

    return {
        "name": perfume['name'].title(),
        "designer": perfume['designer'].title(),
        "gender": perfume['gender'].capitalize(),
        "rating": f"{perfume['rating']}/5",
        "description": format_text(perfume['description']),
        "season": perfume['season'].capitalize(),
        "top_notes": format_notes(perfume.get('top notes', [])),
        "mid_notes": format_notes(perfume.get('mid notes', [])),
        "base_notes": format_notes(perfume.get('base notes', [])),
        "longevity": perfume['longevity'].capitalize(),
        "sillage": perfume['sillage'].capitalize(),
        "pricevalue": perfume['pricevalue'].capitalize(),
        "link": perfume.get('url', ''),
        "image": perfume.get('image', '')
    }

@app.route('/')
def homepage():
    return render_template('home.html')

@app.route('/chatbot')
def chatbot():
    return render_template('index.html', perfume_data=perfume_data, fragrance_notes=fragrance_notes)

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Form-based perfume recommendation route
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    designers = sorted(set(p['designer'].title() for p in perfume_data))

    if request.method == 'POST':
        selected_designer = request.form.get('designer')
        selected_gender = request.form.get('gender')
        selected_season = request.form.get('season')

        filtered_perfumes = [
            p for p in perfume_data
            if (selected_designer.lower() in p['designer'].lower() if selected_designer else True) and
               (selected_gender.lower() in p['gender'].lower() if selected_gender else True) and
               (selected_season.lower() in p['season'].lower() if selected_season else True)
        ]

        formatted_perfumes = [format_perfume_response(p) for p in filtered_perfumes]
        no_recommendations = len(formatted_perfumes) == 0

        return render_template('recommend.html',
                               perfumes=formatted_perfumes,
                               designers=designers,
                               no_recommendations=no_recommendations)

    return render_template('recommend.html', perfumes=[], designers=designers, no_recommendations=False)

# Main chatbot route for handling user queries
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.form['user_input'].lower()

        # Checking if user is asking about a specific perfume
        intent_match = re.search(
            r"(tell me about|describe|what can you say about|give me details about|talk about)\s+(.*)",
            user_input, re.IGNORECASE)
        if intent_match:
            perfume_name = intent_match.group(2).strip()
            perfume_details = find_perfume_by_name(perfume_name)
            if perfume_details:
                return jsonify({"structured": perfume_details})

        # Extracting and matching user preferences
        criteria = extract_preferences(user_input)
        if criteria:
            recommendations = recommend_perfumes_by_criteria(criteria)
            if recommendations:
                return jsonify({"structured": recommendations})

        # Fallback to GPT response
        response = fine_tuned_gpt(user_input)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GPT logic if no structured response found or for general queries
def fine_tuned_gpt(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="ft:gpt-4o-2024-08-06:personal::AjoMgZCP",
            messages=[
                {"role": "system",
                 "content": "You are a knowledgeable and friendly perfume consultant specializing in UAE perfumes only."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception:
        return "I'm sorry, but I couldn't process your request right now. Please try again later."

if __name__ == '__main__':
    app.run(debug=False)
