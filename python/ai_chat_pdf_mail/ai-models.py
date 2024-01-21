import os
import openai
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_KEY')
openai.api_key = api_key
#returns a list of all OpenAI models
models = openai.Model.list()
print(models)

# converts the list of OpenAI models to a Pandas DataFrame
import pandas as pd
data = pd.DataFrame(models["data"])
data.head(20)
