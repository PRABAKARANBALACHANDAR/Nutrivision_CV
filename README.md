# Food Nutrition Analyzer

A web application that uses Google's Gemini API to analyze food images and provide nutritional information.

## Features

- Upload food images from both mobile and desktop devices
- Recognize food items in the image
- Estimate portion sizes
- Calculate approximate calories
- Analyze macronutrients (carbs, proteins, fats)
- Identify potential dietary concerns

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and visit `http://localhost:5000`

## Usage

1. Click the upload button or drag and drop an image of your food
2. Click "Analyze Food" to process the image
3. View the detailed nutritional analysis results

## Note

You'll need to obtain a Google API key from the Google Cloud Console and enable the Gemini API to use this application.
