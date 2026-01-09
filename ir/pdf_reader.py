import os
import json
import re
from pdfminer.high_level import extract_text

DATASET_DIR = "dataset/jurnal"
OUTPUT_FILE = "processed/paragraphs.json"

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def is_noise_paragraph(p):
    p_upper = p.upper()
    noise_keywords = [
        "DAFTAR PUSTAKA",
        "REFERENCES",
        "BIBLIOGRAPHY",
        "ISSN",
        "DOI:",
        "COPYRIGHT"
    ]
    return any(k in p_upper for k in noise_keywords)

def split_paragraphs(text):
    # Gabung baris rusak
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    paragraphs = []
    buffer = ""

    for line in lines:
        # Judul BAB dianggap paragraf baru
        if re.match(r"(BAB|Bab|CHAPTER)", line):
            if buffer:
                paragraphs.append(clean_text(buffer))
                buffer = ""
            paragraphs.append(line)
            continue

        buffer += " " + line

        # Jika buffer cukup panjang → simpan
        if len(buffer.split()) > 40:
            paragraphs.append(clean_text(buffer))
            buffer = ""

    if buffer:
        paragraphs.append(clean_text(buffer))

    # filter akhir
    final_paragraphs = []
    for p in paragraphs:
        if len(p.split()) < 15:
            continue
        if is_noise_paragraph(p):
            continue
        final_paragraphs.append(p)

    return final_paragraphs


all_paragraphs = []
pid = 1

for file in os.listdir(DATASET_DIR):
    if file.lower().endswith(".pdf"):
        path = os.path.join(DATASET_DIR, file)
        text = extract_text(path)

        if not text or len(text.strip()) < 100:
            print(f"⚠️ Gagal baca PDF: {file}")
            continue

        paragraphs = split_paragraphs(text)

        for p in paragraphs:
            all_paragraphs.append({
                "id": pid,
                "paragraph": p,
                "jurnal": file
            })
            pid += 1

os.makedirs("processed", exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_paragraphs, f, indent=2, ensure_ascii=False)

print(f"✅ Selesai. Total paragraf disimpan: {len(all_paragraphs)}")
