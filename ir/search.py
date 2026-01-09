import json
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from ir.preprocessing import preprocess
from nltk.tokenize import sent_tokenize
import nltk
import re
import os

nltk.download("punkt")

TFIDF_FILE = "index/tfidf_matrix.pkl"
VECTORIZER_FILE = "index/vectorizer.pkl"
PARAGRAPH_FILE = "processed/paragraphs.json"


def load_index():
    """
    🔥 WAJIB load ulang setiap search
    """
    if not os.path.exists(TFIDF_FILE):
        return None, None, None

    with open(TFIDF_FILE, "rb") as f:
        tfidf_matrix = pickle.load(f)

    with open(VECTORIZER_FILE, "rb") as f:
        vectorizer = pickle.load(f)

    with open(PARAGRAPH_FILE, "r", encoding="utf-8") as f:
        paragraphs = json.load(f)

    return tfidf_matrix, vectorizer, paragraphs


def summarize_paragraph(paragraph, vectorizer, n_sentences=2):
    sentences = sent_tokenize(paragraph)

    if len(sentences) <= n_sentences:
        return paragraph

    sentence_vectors = vectorizer.transform(
        [preprocess(s) for s in sentences]
    )

    scores = sentence_vectors.sum(axis=1).A1
    top_idx = scores.argsort()[::-1][:n_sentences]
    top_idx = sorted(top_idx)

    return " ".join([sentences[i] for i in top_idx])


def highlight_text(text, query):
    keywords = preprocess(query).split()
    highlighted = text

    for kw in set(keywords):
        if len(kw) < 3:
            continue
        highlighted = re.sub(
            rf"\b({re.escape(kw)})\b",
            r"<mark>\1</mark>",
            highlighted,
            flags=re.IGNORECASE
        )

    return highlighted


def search(query, top_k=50):  # Changed from 3 to 50
    tfidf_matrix, vectorizer, paragraphs = load_index()

    if tfidf_matrix is None:
        return []

    query_processed = preprocess(query)
    query_vec = vectorizer.transform([query_processed])

    similarities = cosine_similarity(query_vec, tfidf_matrix)[0]

    # 🔥 FILTER YANG SCORE 0
    ranked_idx = [
        i for i in similarities.argsort()[::-1]
        if similarities[i] > 0
    ][:top_k]

    results = []
    for rank, idx in enumerate(ranked_idx):
        para = paragraphs[idx]["paragraph"]

        results.append({
            "paragraph": highlight_text(para, query),
            "summary": highlight_text(
                summarize_paragraph(para, vectorizer), query
            ),
            "jurnal": paragraphs[idx]["jurnal"],
            "score": float(similarities[idx]),
            "rank": rank + 1  # Add rank number
        })

    return results


if __name__ == "__main__":
    q = input("Masukkan pertanyaan: ")
    res = search(q)

    for r in res:
        print("\n=== HASIL PENCARIAN ===")
        print("Jurnal :", r["jurnal"])
        print("Score  :", r["score"])
        print("Rank   :", r["rank"])
        print("Ringkasan:")
        print(r["summary"])