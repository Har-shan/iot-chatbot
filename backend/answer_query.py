# import json
# import requests
# import chromadb
# from sentence_transformers import SentenceTransformer
# from chromadb.config import Settings


# chroma_client = chromadb.PersistentClient(path="../chroma_db")
# collection = chroma_client.get_or_create_collection("iot_collection")


# model = SentenceTransformer("all-MiniLM-L6-v2")


# API_URL = "https://api.together.xyz/inference"
# API_KEY = "tgp_v1_6FdzehYp8DTqgDGi4mhydumoysGax-MrWm5Yfc0m6NE"  

# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# def ask(question: str) -> str:
#     try:
#         print(f"[Incoming Question]: {question}")

        
#         question_embedding = model.encode([question])[0]

        
#         results = collection.query(
#             query_embeddings=[question_embedding],
#             n_results=5
#         )

#         documents = results.get("documents", [[]])[0]
#         context = "\n".join(documents)

#         prompt = f"""
# You are a helpful assistant for answering IoT-related questions.
# Use the provided context to answer the question. If the context is insufficient, rely on general knowledge.

# Context:
# {context}

# Question: {question}
# Answer:
# """

#         payload = {
#             "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
#             "prompt": prompt,
#             "max_tokens": 512,
#             "temperature": 0.7,
#             "top_p": 0.9
#         }

#         print("[Sending prompt to Together API]")
#         response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

#         if response.status_code != 200:
#             print("API Error:", response.text)
#             return "Error: Failed to get response from model API."

#         result = response.json()
#         print("[Raw API Response]:", result)

        
#         output = (
#             result.get("output") or
#             result.get("generated_text") or
#             result.get("choices", [{}])[0].get("text") or
#             "Sorry, no response returned."
#         )

#         print("[API Model Response]:", output[:200])
#         return output

#     except Exception as e:
#         print("Error in ask():", str(e))
#         return "An error occurred while processing your question."


# import json
# import requests
# import chromadb
# from sentence_transformers import SentenceTransformer
# from chromadb.config import Settings
# from pymongo import MongoClient
# from datetime import datetime


# chroma_client = chromadb.PersistentClient(path="../chroma_db")
# collection = chroma_client.get_or_create_collection("iot_collection")


# model = SentenceTransformer("all-MiniLM-L6-v2")


# API_URL = "https://api.together.xyz/inference"
# API_KEY = "tgp_v1_6FdzehYp8DTqgDGi4mhydumoysGax-MrWm5Yfc0m6NE"
# headers = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }


# MONGO_URI = "mongodb+srv://rathodharshan7:1494993@cluster0.pdwsmxq.mongodb.net/?retryWrites=true&w=majority"
# mongo_client = MongoClient(MONGO_URI)
# mongo_db = mongo_client["iot_chatbot"]
# qa_collection = mongo_db["qa_logs"]  

# def ask(question: str) -> str:
#     try:
#         print(f"[Incoming Question]: {question}")

        
#         question_embedding = model.encode([question])[0]

        
#         results = collection.query(query_embeddings=[question_embedding], n_results=5)
#         documents = results.get("documents", [[]])[0]
#         context = "\n".join(documents)

       
#         prompt = f"""
# You are a helpful assistant for answering IoT-related questions.
# Use the provided context to answer the question. If the context is insufficient, rely on general knowledge.

# Context:
# {context}

# Question: {question}
# Answer:
# """
#         payload = {
#             "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
#             "prompt": prompt,
#             "max_tokens": 512,
#             "temperature": 0.7,
#             "top_p": 0.9
#         }

#         print("[ Sending prompt to Together API]")
#         response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

#         if response.status_code != 200:
#             print("API Error:", response.text)
#             return "Error: Failed to get response from model API."

#         result = response.json()
#         output = (
#             result.get("output") or
#             result.get("generated_text") or
#             result.get("choices", [{}])[0].get("text") or
#             "Sorry, no response returned."
#         ).strip()

#         print("[API Response]:", output[:200])

      
#         qa_collection.insert_one({
#             "question": question,
#             "answer": output,
#             "context": documents,
#             "timestamp": datetime.now(),
#             "feedback": None  
#         })

#         return output

#     except Exception as e:
#         print("❌ Error in ask():", str(e))
#         return "An error occurred while processing your question."



import os
import json
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
# --- Setup ChromaDB ---
chroma_client = chromadb.PersistentClient(path="../chroma_db")
collection = chroma_client.get_or_create_collection("iot_collection")

# --- Sentence embedding model ---
embedding_model = SentenceTransformer("all-MiniLM-L12-v2")

# --- Together API ---
API_URL = "https://api.together.xyz/inference"
API_KEY = os.getenv("TOGETHER_API_KEY") 
if not API_KEY:
    raise ValueError("Missing TOGETHER_API_KEY in environment.") 
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- MongoDB setup ---
MONGO_URI =os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["iot_chatbot"]
qa_collection = db["qa_logs"]

def clean_and_filter_context(chunks, min_length=30):
    """Remove duplicates and short texts from retrieved chunks."""
    seen = set()
    filtered = []
    for text in chunks:
        cleaned = text.strip()
        if len(cleaned) >= min_length and cleaned not in seen:
            filtered.append(cleaned)
            seen.add(cleaned)
    return filtered

def build_prompt(context, question):
    """Craft a clear, strong system-level prompt for Together API."""
    return f"""
# System
You are an expert IoT assistant. Use the given context below to answer the question precisely and concisely. 
Avoid making up information. If unsure, clearly say "I don't know from the context."

# Context
{context}

# Question
{question}

# Answer
"""

def ask(question: str) -> str:
    try:
        print(f"\n[Incoming Question]: {question}")

        # --- Embedding the question ---
        question_embedding = embedding_model.encode([question])[0]

        # --- Query top 10 chunks from ChromaDB ---
        results = collection.query(query_embeddings=[question_embedding], n_results=10)
        documents = results.get("documents", [[]])[0]

        # --- Filter & clean ---
        context_chunks = clean_and_filter_context(documents)
        context_text = "\n\n".join(context_chunks)

        if not context_text.strip():
            print("⚠ Warning: Empty context found. Using fallback note.")
            context_text = "No relevant context found. Please rely on general IoT knowledge."

        # --- Build prompt ---
        final_prompt = build_prompt(context_text, question)

        # --- Prepare API payload ---
        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "prompt": final_prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }

        print("[🛰 Sending prompt to Together API...]")
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=120)

        if response.status_code != 200:
            print("API Error:", response.text)
            return "Error: Failed to get response from Together API."

        result = response.json()
        output = (
            result.get("output") or
            result.get("generated_text") or
            result.get("choices", [{}])[0].get("text") or
            "Sorry, no response returned."
        ).strip()

        print("[API Response]:", output[:200])

        # --- Save log ---
        qa_collection.insert_one({
            "question": question,
            "answer": output,
            "context_snippet": context_chunks[:5],  # Save first 5 for logs
            "timestamp": datetime.utcnow(),
            "feedback": None
        })

        return output

    except Exception as e:
        print("Error in ask():", str(e))
        return "An unexpected error occurred while processing your question."