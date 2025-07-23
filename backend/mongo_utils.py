
from pymongo import MongoClient
from datetime import datetime

# Insert your actual MongoDB URI here later
MONGO_URI = "mongodb+srv://rathodharshan7:1494993@cluster0.pdwsmxq.mongodb.net/?retryWrites=true&w=majority&tls=true"
DB_NAME = "iot_chatbot"
COLLECTION_QA = "questions_answers"
COLLECTION_FEEDBACK = "feedback"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

def log_question_answer(question, answer):
    db[COLLECTION_QA].insert_one({
        "question": question,
        "answer": answer,
        "timestamp": datetime.utcnow()
    })

def log_feedback(question, liked):
    db[COLLECTION_FEEDBACK].insert_one({
        "question": question,
        "liked": liked,
        "timestamp": datetime.utcnow()
    })



