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
data['COST'] = 0.0

# Iterate over each model and test it
for model_id in data.index:
    try:
        with openai.ChatCompletion.create_callback() as cb:
            response = openai.ChatCompletion.create(model=model_id, messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is the capital of Norway?"}])
            if "Oslo" in response['choices'][0]['message']['content']:
                data.loc[model_id, 'CHECK'] = 'OSLO'
                data.loc[model_id, 'COST'] = cb.usage['total_tokens'] * 0.0002 # assuming a rate of $0.0002 per token
    except Exception as e:
        pass

# Reorder the columns to place 'CHECK' and 'COST' as the second and third columns
data = data[['CHECK', 'COST', 'created', 'owned_by']]

table = data.to_markdown()
line_length = max(len(line) for line in table.split("\n"))

print('─' * line_length)
print("Current Date and Time: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print('─' * line_length)
print(table)
print('─' * line_length)
