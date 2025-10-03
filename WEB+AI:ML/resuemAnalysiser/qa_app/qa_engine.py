import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# Split text into sentences/chunks

def split_into_chunks(text, chunk_size=3):
    # Split by sentences, then group into chunks of N sentences
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = [' '.join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)]
    return [c.strip() for c in chunks if c.strip()]

# Extract text from PDF

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() or ''
    return text

# Embed a list of texts

def embed_texts(texts):
    return MODEL.encode(texts)

# Retrieve top-k relevant chunks

def retrieve_chunks(question, chunks, chunk_embeddings, top_k=3):
    q_emb = MODEL.encode([question])
    sims = cosine_similarity(q_emb, chunk_embeddings)[0]
    top_idx = np.argsort(sims)[::-1][:top_k]
    return [chunks[i] for i in top_idx]
