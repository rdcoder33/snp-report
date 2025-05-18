from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_perplexity import ChatPerplexity

from dotenv import load_dotenv

import os

load_dotenv()

strict_llm = ChatOpenAI(model="gpt-4.1", temperature=0, max_tokens=32768)
creative_llm = ChatOpenAI(model="gpt-4.1", temperature=0.7, max_tokens=32768)


chat_perplexity = ChatPerplexity(
    temperature=0.7, 
    api_key=os.getenv("PPLX_API_KEY"),
    model="sonar-pro",
    
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")