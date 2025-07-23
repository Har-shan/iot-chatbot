import json
import os
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# --- Load JSON data ---
json_path = os.path.join(os.path.dirname(__file__), "..", "data", "iot_scraped.json")

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Extract and clean texts ---
raw_texts = [item.get("text", "").strip() for item in data if item.get("text", "").strip()]
print(f"[INFO] Total raw chunks loaded: {len(raw_texts)}")

# --- Remove duplicates ---
unique_texts = list(set(raw_texts))
print(f"[INFO] Unique texts after deduplication: {len(unique_texts)}")

# --- Filter too-short texts ---
clean_texts = [t for t in unique_texts if len(t) >= 30]
print(f"[INFO] Texts after filtering too-short entries: {len(clean_texts)}")

# --- Optionally chunk very large texts (split to 500 chars) ---
final_texts = []
for text in clean_texts:
    if len(text) > 1000:
        for i in range(0, len(text), 500):
            chunk = text[i:i+500].strip()
            if len(chunk) >= 30:
                final_texts.append(chunk)
    else:
        final_texts.append(text)

print(f"[INFO] Final chunked texts count: {len(final_texts)}")

# --- Load embedding model ---
model = SentenceTransformer("all-MiniLM-L12-v2")

# --- Encode embeddings with progress bar ---
print("[*] Generating embeddings...")
embeddings = model.encode(final_texts, show_progress_bar=True).tolist()

# --- Setup ChromaDB ---
chroma_client = chromadb.PersistentClient(path="../chroma_db")
collection_name = "iot_collection"
collection = chroma_client.get_or_create_collection(name=collection_name)

# --- Clear old data safely ---
try:
    collection.delete(ids="all")  # Delete all existing entries
    print("[*] Existing collection data cleared successfully.")
except Exception as e:
    print(f"[!] Warning while deleting existing data: {e}")


# --- Batch add (to avoid large single push errors) ---
batch_size = 5000
print("[*] Adding documents in batches to ChromaDB...")

for i in tqdm(range(0, len(final_texts), batch_size)):
    batch_docs = final_texts[i:i+batch_size]
    batch_embeddings = embeddings[i:i+batch_size]
    batch_ids = [f"id_{i + j}" for j in range(len(batch_docs))]
    collection.add(
        documents=batch_docs,
        embeddings=batch_embeddings,
        ids=batch_ids
    )

print(f"\nSuccessfully stored {len(final_texts)} cleaned and chunked texts into ChromaDB.\n")