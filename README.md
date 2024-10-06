## Sentiment Analysis API with LLM Integration

Developed a Flask-based API that processes customer reviews into CSV and XLSX files, performs sentiment analysis using a Large Language Model, and returns structured results.

## Features
- Upload CSV or XLSX files with customer reviews.
- Analyze the sentiment (positive, neutral, or negative) of each review using the Groq API.
- Display a summary of positive, negative, and neutral reviews.
- User-friendly interface styled with Bootstrap for a clean and responsive design.

## Technologies Used
- **Flask**: Micro Web framework for building the API and web app.
- **Pandas**: For processing CSV and XLSX files.
- **Groq API**: To perform sentiment analysis.
- **Bootstrap**: For styling the web interface.

## Setup Instructions

### Prerequisites
- Python 3.8+
- A Groq API Key (click [here](https://console.groq.com/))
- Git

## Check Requirements.txt file

- install all dependencies
- use this command pip install -r requirements.txt

## Must Create virtual environment

- use this command pip install python -m venv myenv "environment_name"

## Keep secret of GROQ API Key in OS Environment Variable

- import Os
- GROQ_API_KEY=your-groq-api-key

## Finally Run Application

- Use python main.py
