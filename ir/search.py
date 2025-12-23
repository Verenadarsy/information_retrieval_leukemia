import json
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from ir.preprocessing import preprocess

TFIDF_FILE = "index/tfidf_matrix.pkl"
VECTORIZER_FILE = "index/vectorizer.pkl"
PARAGRAPH_FILE = "processed/paragraphs.json"

with open(TFIDF_FILE, "rb") as f:
    tfidf_matrix = pickle.load(f)

with open(VECTORIZER_FILE, "rb") as f:
    vectorizer = pickle.load(f)

with open(PARAGRAPH_FILE, "r", encoding="utf-8") as f:
    paragraphs = json.load(f)

def search(query, top_k=1):
    query_processed = preprocess(query)
    query_vec = vectorizer.transform([query_processed])
    similarities = cosine_similarity(query_vec, tfidf_matrix)
    top_idx = similarities[0].argsort()[::-1][:top_k]
    results = []
    for idx in top_idx:
        results.append({
            "paragraph": paragraphs[idx]["paragraph"],
            "jurnal": paragraphs[idx]["jurnal"],
            "score": float(similarities[0][idx])
        })
    return results

if __name__ == "__main__":
    q = input("Masukkan pertanyaan: ")
    res = search(q)
    for r in res:
        print(f"{r['paragraph']} ({r['jurnal']}) - score: {r['score']:.3f}")
