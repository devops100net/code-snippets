import openai
import os

# Load the OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_daily_news_summary():
    # Prompt the OpenAI model to generate a summary of today's news
    prompt = "Write a summary of the most important news stories from today."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated to use a supported model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Retrieve daily news summary
daily_news_summary = get_daily_news_summary()

if daily_news_summary:
    print("Daily News Summary:\n", daily_news_summary)
else:
    print("Failed to retrieve the news summary.")

