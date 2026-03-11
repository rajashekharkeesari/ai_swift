from langchain_core.prompts import PromptTemplate
from src.reranker import predict_reranker
from src.prompt import PROMPT
from src.retriver import visa_retriver_instance
from src.llm_model import llm
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

def prompt_formater(query, k):
   prompt = PromptTemplate.from_template(PROMPT)
   docs = visa_retriver_instance.similarity_search(query, k)
   retrieved_text = "\n\n".join([doc.page_content for doc in docs])
   reranked_docs = predict_reranker(query,docs)
   print("--------rerankeddoc used for llm is______ ")
   print(f" here the the {reranked_docs[0][1].page_content}")
   final_prompt = prompt.format(user_input=query,  retrieved_documents=reranked_docs[0])
   return final_prompt,retrieved_text,reranked_docs



