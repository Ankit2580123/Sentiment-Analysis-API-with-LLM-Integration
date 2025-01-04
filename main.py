import os
from flask import Flask, request,render_template, redirect, url_for, flash
import pandas as pd
from werkzeug.utils import secure_filename
import requests
import time

app = Flask(__name__)
app.secret_key = "secret_key"  # Needed for flashing messages (like success/error)


API_KEY = os.environ.get("GROQ_API_KEY")
# api_key="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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-8b-8192"# Default model for sentiment analysis


#Define allowed file types
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# Function to check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 




# Function to process the uploaded file format 
#Tested Working Well
def process_file(file):
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    if 'Review' not in df.columns:
        return None, "Missing 'Review' column in file."
    
    reviews = df['Review'].dropna().tolist()
    # print(reviews)
    return reviews,None


#Function to classify the sentiment and return positive, negative, or neutral anyone, if function called
def classify_sentiment(sentiment_content):
    sentiment_content_lower = sentiment_content.lower()
    if 'positive' in sentiment_content_lower:
        return 'positive'
    elif 'negative' in sentiment_content_lower:
        return 'negative'
    else:
        return 'neutral'


#Analyzing sentiments using Groq Api
def analyze_sentiment(review):
    # print(review)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "user",
                "content": f"Analyze the sentiment of this review: '{review}'"
            }
        ]
    }
   
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError for non-200 status codes
            response_data = response.json()
        
        # Check if the expected fields are in the response
            if 'choices' in response_data and len(response_data['choices']) > 0:
                sentiment_content = response_data['choices'][0]['message']['content']
                return {"sentiment": sentiment_content}
                # print(sentiment_content)
            else:
                print("Unexpected response structure:", response_data)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"Rate limit reached. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)  # delay execution for a given number of seconds.
            else:
                return {"error": str(e)}

        #if api not work then throw this exception
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        
   
    return {"error": "Failed after multiple retries due to rate limiting."}
           



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file format part
        # print("post")
        if 'file' not in request.files:
            flash('No file Format part! Please Enter Only required format')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            #if file are not selected in this case but javascript validation also worked, this part is optional
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):  #both conditions must be true
            filename = secure_filename(file.filename)

            reviews,error = process_file(file)
            if error:
                    flash(error)
                    return redirect(request.url)
        
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            results = []

            # counter = 1
            for review in reviews:
                # print(review)
                sentiment_result = analyze_sentiment(review)
                # print(sentiment_result['sentiment'])
                
                sentiment = classify_sentiment(sentiment_result['sentiment'])
                
            # Count sentiment classification
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1

                results.append({
                    "review": review,
                    "sentiment": sentiment_result
                })
                
                # counter+=1

                #This print statements used for testing purpose only if you want to check execution in terminal so you can uncomment.
                # print(positive_count,negative_count,neutral_count)
                # print("counter: ",counter)


           # print(positive_count,negative_count,neutral_count)
           # Calculate total reviews and percentages and round 2 digit only
            total_reviews = len(reviews)
            positive_score = round(positive_count / total_reviews, 2)
            negative_score = round(negative_count / total_reviews, 2)
            neutral_score = round(neutral_count / total_reviews, 2)
            
            # Create the Score Dictionary
            sentiment_dict = {
                "positive": positive_score,
                "negative": negative_score,
                "neutral": neutral_score
            }
            #create a total dictionary which store total reviews,total positive and so on.
            total={
                "total_reviews":total_reviews,
                "total_positive_count":positive_count,
                "total_negative_count":negative_count,
                "total_neutral_count":neutral_count

            }

            # Pass results and sentiment summary to the template to be displayed
            return render_template('analysis_result.html', results=results, summary=sentiment_dict,
                                  total_summary=total
                                   )
        
        else:
            flash('Allowed file types are CSV, XLSX')
            return redirect(request.url)
  
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)