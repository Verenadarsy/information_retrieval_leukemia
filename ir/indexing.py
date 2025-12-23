import json
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

INPUT_FILE = "processed/paragraphs_preprocessed.json"
TFIDF_FILE = "index/tfidf_matrix.pkl"
VECTORIZER_FILE = "index/vectorizer.pkl"

os.makedirs("index", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    paragraphs = json.load(f)

docs = [p["processed"] for p in paragraphs]

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(docs)

# Simpan
with open(TFIDF_FILE, "wb") as f:
    pickle.dump(tfidf_matrix, f)

with open(VECTORIZER_FILE, "wb") as f:
    pickle.dump(vectorizer, f)

print("Indexing selesai, TF-IDF matrix & vectorizer tersimpan.")
