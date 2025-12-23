import os
import json
from PyPDF2 import PdfReader

INPUT_FOLDER = "dataset/jurnal"
OUTPUT_FILE = "processed/paragraphs.json"

os.makedirs("processed", exist_ok=True)

paragraphs = []

for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".pdf"):
        file_path = os.path.join(INPUT_FOLDER, filename)
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        # Pecah teks menjadi paragraf berdasarkan double newline
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                paragraphs.append({
                    "jurnal": filename,
                    "paragraph": para
                })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(paragraphs, f, indent=2, ensure_ascii=False)

print(f"Ekstraksi selesai, {len(paragraphs)} paragraf tersimpan di {OUTPUT_FILE}")
