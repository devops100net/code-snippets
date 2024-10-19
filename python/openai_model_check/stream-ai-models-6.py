import streamlit as st
import os
import openai
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load .env environment variables
load_dotenv()

# Check if the API key is set in the environment
env_api_key = os.getenv('OPENAI_API_KEY')

# Function to run the model check
def run_model_check(api_key):
    openai.api_key = api_key

    # Retrieve models from OpenAI and store in DataFrame
    models = openai.Model.list()
    data = pd.DataFrame(models["data"])

    # Convert 'created' column to a datetime format and display it in the desired format
    data['created'] = pd.to_datetime(data['created'], unit='s').dt.strftime("%Y-%m-%d %H:%M")

    # Set 'id' as the index
    data.set_index('id', inplace=True)

    # Sort the data by 'owned_by' and 'created' in descending order
    data.sort_values(by=['owned_by', 'created'], ascending=[False, False], inplace=True)

    # Initialize a new column 'CHECK' with default value 'NO'
    data['CHECK'] = 'NO'

    # Progress bar setup
    progress_bar = st.progress(0)
    total_models = len(data)
    checked_models = 0

    # Iterate over each model and test it
    for model_id in data.index:
        try:
            response = openai.ChatCompletion.create(model=model_id, messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of Norway?"}])
            if "Oslo" in response['choices'][0]['message']['content']:
                data.loc[model_id, 'CHECK'] = 'OSLO'
        except Exception as e:
            pass
        checked_models += 1
        progress_bar.progress(checked_models / total_models)

    # Reorder the columns to place 'CHECK' as the second column
    data = data[['CHECK', 'object', 'created', 'owned_by']]

    # Display the table in Streamlit
    st.write("Current Date and Time: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.dataframe(data)

# Streamlit webpage title
st.title("OpenAI Model Checker")

if env_api_key:
    # If API key is available in environment, run the model check automatically
    run_model_check(env_api_key)
else:
    # If API key is not available, ask for it in the UI
    user_api_key = st.text_input("Enter OpenAI API Key:", type="password")
    run_button = st.button("Run Model Check")
    if run_button and user_api_key:
        run_model_check(user_api_key)

