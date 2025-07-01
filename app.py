import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables")

# Configure Gemini model
try:
    genai.configure(api_key=api_key)
    current_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    raise RuntimeError(f"Failed to configure Gemini API: {str(e)}")

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('food_logs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS meal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            meal_data TEXT,
            health_score REAL
        )
    ''')
    conn.commit()
    conn.close()

def extract_json_from_response(text):
    """Extract JSON from response text that might contain markdown code blocks."""
    # Try to find JSON between code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        text = text[start:end].strip()
    return text.strip()

def format_nutrition_data(json_data):
    """Format the nutrition data into a structured report."""
    return {
        "foods_identified": {
            "title": "Foods Identified",
            "items": json_data.get("foods", [])
        },
        "serving_info": {
            "title": "Serving Information",
            "portions": json_data.get("portions", ["Not specified"])[0]
        },
        "nutrition_facts": {
            "title": "Nutrition Facts",
            "calories": f"{json_data.get('calories', 0)} kcal",
            "macros": {
                "Carbohydrates": f"{json_data.get('macronutrients', {}).get('carbs', 0)}g",
                "Proteins": f"{json_data.get('macronutrients', {}).get('proteins', 0)}g",
                "Fats": f"{json_data.get('macronutrients', {}).get('fats', 0)}g"
            }
        },
        "health_notes": {
            "title": "Dietary Considerations",
            "concerns": json_data.get("dietary_concerns", [])
        }
    }

def format_nutrition_data_text(json_data):
    """Format the nutrition data into readable text."""
    foods = '\n  - '.join(json_data.get('foods_identified', {}).get('items', []))
    concerns = '\n  - '.join(json_data.get('health_notes', {}).get('concerns', []))
    macros = json_data.get('nutrition_facts', {}).get('macros', {})
    
    report = f"""
Foods Identified:
  - {foods}

Serving Information:
  {json_data.get('serving_info', {}).get('portions', 'Not specified')}

Nutrition Facts:
  Calories: {json_data.get('nutrition_facts', {}).get('calories', '0 kcal')}
  Carbohydrates: {macros.get('Carbohydrates', '0g')}
  Proteins: {macros.get('Proteins', '0g')}
  Fats: {macros.get('Fats', '0g')}

Dietary Considerations:
  - {concerns}
"""
    return report.strip()

def calculate_health_score(foods):
    """Calculate a health score from 0-10 based on nutritional balance"""
    score = 7.0  # Base score
    # Adjust based on food variety, nutrients, etc
    if len(foods) >= 3:
        score += 1.0  # Bonus for variety
    # Add more scoring logic
    return min(10.0, max(0.0, score))

def analyze_food_image(image):
    try:
        prompt = """Analyze this food image and provide ONLY a JSON object with the following information:
        {
            "foods": [{
                "name": "food name",
                "confidence": "confidence percentage",
                "origin": "cultural origin and brief description",
                "position": {"x": 0, "y": 0, "width": 0, "height": 0},
                "nutrition": {
                    "calories": 0,
                    "carbs": 0,
                    "proteins": 0,
                    "fats": 0,
                    "serving_size": "portion description",
                    "serving_multiplier": 1
                },
                "allergens": ["list of allergens"],
                "dietary_labels": ["list of dietary labels"],
                "healthy_alternatives": ["list of suggestions"],
                "health_benefits": ["list of health benefits"]
            }],
            "total": {
                "calories": 0,
                "carbs": 0,
                "proteins": 0,
                "fats": 0
            },
            "daily_values": {
                "calorie_percentage": 0
            },
            "health_score": 0,
            "health_benefits": ["list of positive aspects"],
            "healthy_alternatives": ["list of improvement suggestions"]
        }"""
        
        response = current_model.generate_content([prompt, image])
        json_text = extract_json_from_response(response.text)
        
        try:
            result = json.loads(json_text)
            return result  # Return raw JSON for frontend processing
        except json.JSONDecodeError:
            raise Exception("Failed to parse nutrition data. Please try again.")
            
    except Exception as e:
        raise Exception(f"Error analyzing image: {str(e)}")

@app.route('/cultural_info/<food_name>', methods=['GET'])
def get_cultural_info(food_name):
    try:
        prompt = f"Provide cultural and historical information about {food_name} in 2-3 sentences."
        response = current_model.generate_content(prompt)
        return jsonify({'info': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    try:
        image = Image.open(image_file)
        result = analyze_food_image(image)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_meal', methods=['POST'])
def save_meal():
    data = request.json
    conn = sqlite3.connect('food_logs.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO meal_logs (date, meal_data, health_score) VALUES (?, ?, ?)',
        (datetime.now().isoformat(), json.dumps(data['meal']), data['score'])
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/meal_history', methods=['GET'])
def get_meal_history():
    conn = sqlite3.connect('food_logs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM meal_logs ORDER BY date DESC LIMIT 10')
    meals = [{'date': row[1], 'meal': json.loads(row[2]), 'score': row[3]} 
             for row in c.fetchall()]
    conn.close()
    return jsonify(meals)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
