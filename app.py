from flask import Flask, render_template, request
import openai
import json
import re

app = Flask(__name__)

# Use your OpenAI API key here
openai.api_key = "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"

# Load perfume dataset into memory
with open("perfume_data.json", "r") as f:
    perfume_data = json.load(f)

# Preprocess the perfume data to include a "notes" string for easy matching
for perfume in perfume_data:
    perfume["notes"] = ', '.join(perfume.get("top notes", []) +
                                 perfume.get("mid notes", []) +
                                 perfume.get("base notes", []))
    perfume["rating"] = f"{perfume['rating']}/5"  # Format rating

# Store conversation history in memory
conversation_history = []

def analyze_query_with_gpt(user_input):
    """Classify query type and extract intent using GPT model."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a knowledgeable and friendly chatbot. Analyze user queries to classify them as recommendations, product-specific, or general queries."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=200
        )
        gpt_response = response['choices'][0]['message']['content'].strip()
        return gpt_response
    except Exception as e:
        return f"Error: {str(e)}"

def search_perfumes_by_keywords(keywords, max_results=3):
    """Search perfumes in the dataset based on extracted keywords."""
    results = []
    for perfume in perfume_data:
        matches = []
        for keyword in keywords:
            if (
                keyword in perfume["name"].lower() or
                keyword in perfume["description"].lower() or
                keyword in perfume["notes"].lower()
            ):
                matches.append(keyword)
        if matches:
            results.append({
                "image": perfume["image"],
                "name": perfume["name"],
                "designer": perfume["designer"],
                "description": perfume["description"],
                "gender": perfume["gender"],
                "rating": perfume["rating"],
                "notes": perfume["notes"],
                "longevity": perfume["longevity"],
                "sillage": perfume["sillage"],
                "price": perfume["pricevalue"],
                "link": perfume["url"],
                "match_count": len(matches)
            })
    # Sort by match count and limit results
    results = sorted(results, key=lambda x: x["match_count"], reverse=True)
    return results[:max_results]

@app.route('/')
def home():
    return render_template('index.html', conversation=conversation_history)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']

    # Step 1: Analyze query type using GPT
    query_analysis = analyze_query_with_gpt(user_input)

    if "recommendation" in query_analysis.lower():
        # Step 2: Extract keywords for recommendations
        # Extract designer names from perfume_data.json
        designers = [perfume["designer"].lower() for perfume in perfume_data]

        # Combine designer names into the regex pattern
        designer_pattern = "|".join(re.escape(designer) for designer in designers)

        # Updated regex with designer names
        keywords = re.findall(
            rf"\b("
            r"long lasting|spicy|fresh|woody|oriental|floral|citrus|gourmand|"
            r"vanilla|amber|musky|fruity|sweet|smoky|oud|luxurious|unisex|bold|powdery|warm|aquatic|"
            r"masculine|feminine|for women|for men|for women and men|"
            r"excellent|good|average|high rating|low rating|"
            r"cinnamon|nutmeg|bergamot|dates|praline|tuberose|mahonial|myrrh|benzoin|akigalawood|"
            r"strong|moderate|enormous|weak|"
            r"affordable|premium|cheap|expensive|value for money|"
            + designer_pattern +  # Dynamically add designers to the pattern
            r")\b",
            user_input.lower()
        )

        matched_perfumes = search_perfumes_by_keywords(keywords)

        if matched_perfumes:
            chatbot_response = {
                "type": "structured",
                "content": matched_perfumes
            }
        else:
            chatbot_response = {
                "type": "text",
                "content": "I couldn't find any perfumes matching your preferences. Try refining your query."
            }

    elif "product-specific" in query_analysis.lower():
        # Step 3: Handle product-specific queries
        keywords = user_input.lower().split()  # Simplistic keyword extraction for product names
        matched_perfumes = search_perfumes_by_keywords(keywords, max_results=1)

        if matched_perfumes:
            chatbot_response = {
                "type": "structured",
                "content": matched_perfumes
            }
        else:
            chatbot_response = {
                "type": "text",
                "content": "I couldn't find the perfume you are asking about. Please refine your query."
            }

    else:
        # Step 4: Handle general queries with GPT
        try:
            response = openai.ChatCompletion.create(
                model="ft:gpt-4o-2024-08-06:personal::AjoMgZCP",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable and friendly perfume consultant specializing in UAE perfumes Only. Provide structured responses the 'structured' key. For general queries, respond conversationally. Always aim to provide accurate and helpful information about UAE perfumes."},
                    *[{"role": "user", "content": entry["user"]} for entry in conversation_history],
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500
            )
            chatbot_response_content = response['choices'][0]['message']['content'].strip()
            chatbot_response = {
                "type": "text",
                "content": chatbot_response_content
            }
        except Exception as e:
            chatbot_response = {
                "type": "text",
                "content": f"I couldn't process your query. Please try again later. (Error: {str(e)})"
            }

    # Add to conversation history
    conversation_history.append({"user": user_input, "response": chatbot_response})
    return render_template('index.html', conversation=conversation_history)

if __name__ == '__main__':
    app.run(debug=True)