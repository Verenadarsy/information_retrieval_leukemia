import os
import json
from pdfminer.high_level import extract_text

DATASET_DIR = "dataset/jurnal"
OUTPUT_FILE = "processed/paragraphs.json"

def is_noise_paragraph(p):
    p_upper = p.upper()
    noise_keywords = [
        "REFERENCES",
        "ACKNOWLEDGEMENTS",
        "ACKNOWLEDGMENTS",
        "BIBLIOGRAPHY",
        "DOI",
        "FIGURE",
        "TABLE",
        "COPYRIGHT",
        "LICENSE",
        "AUTHOR",
        "JOURNAL",
        "ISSN"
    ]
    return any(k in p_upper for k in noise_keywords)

def split_paragraphs(text):
    raw_paragraphs = text.split("\n\n")
    paragraphs = []

    for p in raw_paragraphs:
        p = p.strip()

        # buang paragraf terlalu pendek
        if len(p.split()) < 30:
            continue

        # buang noise (references, dll)
        if is_noise_paragraph(p):
            continue

        paragraphs.append(p)

    return paragraphs

all_paragraphs = []
pid = 1

for file in os.listdir(DATASET_DIR):
    if file.endswith(".pdf"):
        path = os.path.join(DATASET_DIR, file)
        text = extract_text(path)

        paragraphs = split_paragraphs(text)

        for p in paragraphs:
            all_paragraphs.append({
                "id": pid,
                "paragraph": p,
                "jurnal": file
            })
            pid += 1

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_paragraphs, f, indent=2, ensure_ascii=False)

print(f"Selesai. Total paragraf bersih: {len(all_paragraphs)}")
