import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-1.5-flash'

def ask_gemini(context, question):
    prompt = f"""
You are a resume and job description assistant. Use the provided context, which may include both a job description (JD) and a candidate resume, to answer the question. If both are present, use both for your answer.

{context}

Question: {question}
Answer:
"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()





