# UAE-FragBot: AI-Powered Perfume Recommendation Web App 🇦🇪🌸

**UAE-FragBot** is an AI-driven web application that personalizes perfume recommendations for users in the UAE. It merges fine-tuned GPT-4o technology with pattern matching to offer a seamless and culturally relevant fragrance discovery experience.

## 💡 Project Overview

Perfume shopping can be overwhelming—especially in a fragrance-rich market like the UAE, where traditional and modern scents intersect. UAE-FragBot simplifies this process using:

- **Conversational Chatbot (GPT-4o)**: Offers intelligent perfume consultations based on user queries.
- **Form-Based Recommendation Engine**: Suggests fragrances using designer, gender, and season filters.
## 🚀 Features

### 🧠 AI Chatbot
 
- Returns conversational and structured responses.
- Specialized in UAE fragrance knowledge and perfumery culture.
- Ideal for enthusiasts and aspiring perfume creators.

### 📋 Recommendation Machine
- Beginner-friendly form: select **designer**, **gender**, and **season**
- Quickly filters matching perfumes from the dataset.


 
## 🛠️ Tech Stack

| Component         | Tech Used                                  |
|------------------|--------------------------------------------|
| Backend API      | Python, Flask, Flask-RESTful               |
| Frontend         | React, HTML, CSS, JavaScript               |
| AI Integration   | Fine-tuned GPT-4o via OpenAI API           |
| Data Processing  | Regex, JSON, JSONL                         |
| Storage Format   | `perfume_data.json`, `fine_tuning_data.jsonl` |

## 📂 Dataset

- `perfume_data.json`: 331 perfumes details scraped from [Fragrantica](https://www.fragrantica.com), including:
  - Name, Designer, Description and image
  - Notes (top, middle, base)
  - Longevity, sillage, rating, season and price value  
- `fine_tuning_data.jsonl`: Custom training examples to align GPT-4o responses to perfume-specific queries.

 

## 🧪 How to Run Locally
- obtain API key from Open AI (https://platform.openai.com/api-keys)
1.  
   ```bash
   git clone git@git.cs.bham.ac.uk:projects-2024-25/ake179.git
   cd UaeFragBot 
   pip install -r requirements.txt
   npm install
   npm start 
   python app.py

## 📈 Future Improvements
🛍️ Add in-app shopping  

🔊 Voice interaction with AI

💬 Chatbot memory to retain past queries

🧠 Integration of olfactory simulation technologies 

🌐 Larger dataset and multilingual support
   
## 🙋 Developer 
Ahmed Khalid KhalafAllah Elkhedir  

 
 