import os
import openai
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = api_key

models = openai.Model.list()

data = pd.DataFrame(models["data"])
data['created'] = pd.to_datetime(data['created'], unit='s')
data.set_index('id', inplace=True)

# Sort the data by 'owned_by' and 'created' in descending order
data.sort_values(by=['owned_by', 'created'], ascending=[False, False], inplace=True)

# Initialize a new column 'CHECK' with default value 'NO'
data['CHECK'] = 'NO'

# Iterate over each model and test it
for model_id in data.index:
    try:
        response = openai.ChatCompletion.create(model=model_id, messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of Norway?"}])
        if "Oslo" in response['choices'][0]['message']['content']:
            data.loc[model_id, 'CHECK'] = 'OSLO'
    except Exception as e:
        pass

# Reorder the columns to place 'CHECK' as the second column
data = data[['CHECK', 'object', 'created', 'owned_by']]

table = data.to_markdown()
line_length = max(len(line) for line in table.split("\n"))

print('─' * line_length)
print("Current Date and Time: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print('─' * line_length)
print(table)
print('─' * line_length)

