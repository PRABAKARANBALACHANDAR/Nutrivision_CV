# Food Nutrition Analyzer

A web application that uses a VAE to analyze food images and provide nutritional information.

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

2. Run the application:
```bash
python app.py
```

3. Open your browser and visit `http://localhost:5000`

## Usage

1. Click the upload button or drag and drop an image of your food
2. Click "Analyze Food" to process the image
3. View the detailed nutritional analysis results

## Note

You'll need to obtain a Google API key from the Google Cloud Console and enable the Gemini API to use this application.
