import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import json

nltk.download('punkt')
nltk.download('punkt_tab')   # <--- tambahkan ini
nltk.download('stopwords')

STOPWORDS = set(stopwords.words('english'))

def preprocess(text):
    # Lowercase
    text = text.lower()
    # Hapus punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize
    tokens = word_tokenize(text)
    # Hapus stopwords
    tokens = [t for t in tokens if t not in STOPWORDS]
    return " ".join(tokens)

def preprocess_paragraphs(input_file="processed/paragraphs.json", output_file="processed/paragraphs_preprocessed.json"):
    with open(input_file, "r", encoding="utf-8") as f:
        paragraphs = json.load(f)

    for p in paragraphs:
        p["processed"] = preprocess(p["paragraph"])

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(paragraphs, f, indent=2, ensure_ascii=False)

    print(f"Preprocessing selesai, tersimpan di {output_file}")

if __name__ == "__main__":
    preprocess_paragraphs()
