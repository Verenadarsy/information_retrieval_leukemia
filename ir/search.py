import json
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from preprocessing import preprocess
from nltk.tokenize import sent_tokenize
import nltk

nltk.download("punkt")

TFIDF_FILE = "index/tfidf_matrix.pkl"
VECTORIZER_FILE = "index/vectorizer.pkl"
PARAGRAPH_FILE = "processed/paragraphs.json"

# Load index
with open(TFIDF_FILE, "rb") as f:
    tfidf_matrix = pickle.load(f)

with open(VECTORIZER_FILE, "rb") as f:
    vectorizer = pickle.load(f)

with open(PARAGRAPH_FILE, "r", encoding="utf-8") as f:
    paragraphs = json.load(f)



def summarize_paragraph(paragraph, n_sentences=2):
    sentences = sent_tokenize(paragraph)

    if len(sentences) <= n_sentences:
        return paragraph

    # TF-IDF tiap kalimat
    sentence_vectors = vectorizer.transform(
        [preprocess(s) for s in sentences]
    )

    # skor = total bobot tf-idf
    scores = sentence_vectors.sum(axis=1).A1

    # ambil kalimat terbaik
    top_idx = scores.argsort()[::-1][:n_sentences]
    top_idx = sorted(top_idx)

    summary = " ".join([sentences[i] for i in top_idx])
    return summary


def search(query, top_k=1):
    query_processed = preprocess(query)
    query_vec = vectorizer.transform([query_processed])

    similarities = cosine_similarity(query_vec, tfidf_matrix)
    top_idx = similarities[0].argsort()[::-1][:top_k]

    results = []
    for idx in top_idx:
        para = paragraphs[idx]["paragraph"]

        results.append({
            "paragraph": para,
            "summary": summarize_paragraph(para),
            "jurnal": paragraphs[idx]["jurnal"],
            "score": float(similarities[0][idx])
        })

    return results


if __name__ == "__main__":
    q = input("Masukkan pertanyaan: ")
    res = search(q, top_k=1)

    for r in res:
        print("\n=== HASIL PENCARIAN ===")
        print(f"Jurnal : {r['jurnal']}")
        print(f"Score  : {r['score']:.3f}")
        print("Ringkasan:")
        print(r["summary"])
