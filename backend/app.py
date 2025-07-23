from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from answer_query import ask
from pymongo import MongoClient
from datetime import datetime
import os
import json
import traceback

# === Flask Setup with Frontend folder ===
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, supports_credentials=True)

# === MongoDB Setup ===
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)

mongo_db = mongo_client["iot_chatbot"]
qa_collection = mongo_db["qa_logs"]
feedback_collection = mongo_db["feedback_logs"]

# === Retrain file path ===
RETRAIN_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "retrain_context.json")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "Missing 'question' in request."}), 400

    try:
        answer = ask(question)

        # Save to MongoDB
        qa_collection.insert_one({
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow(),
            "feedback": None
        })

        return jsonify({"answer": answer})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")
    feedback_type = data.get("feedback")

    if not all([question, answer, feedback_type]):
        return jsonify({"error": "Missing fields in feedback."}), 400

    try:
        # Save feedback to MongoDB
        feedback_collection.insert_one({
            "question": question,
            "answer": answer,
            "feedback": feedback_type,
            "timestamp": datetime.utcnow()
        })

        qa_collection.update_one(
            {"question": question, "answer": answer},
            {"$set": {"feedback": feedback_type}}
        )

        # Save positive feedback to retrain file
        if feedback_type == "like":
            retrain_data = []

            # Read safely if file exists and is non-empty
            if os.path.exists(RETRAIN_FILE) and os.path.getsize(RETRAIN_FILE) > 0:
                with open(RETRAIN_FILE, "r", encoding="utf-8") as f:
                    try:
                        retrain_data = json.load(f)
                    except json.JSONDecodeError:
                        retrain_data = []

            retrain_data.append({"text": f"Q: {question}\nA: {answer}"})

            with open(RETRAIN_FILE, "w", encoding="utf-8") as f:
                json.dump(retrain_data, f, indent=2)

        return jsonify({"status": "success"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# === Serve Frontend ===
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)