import os
import openai
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('OPENAI_KEY')
openai.api_key = api_key

# Returns a list of all OpenAI models
models = openai.api_resources.model.Model.list()
print(models)

