import json

with open("processed/paragraphs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Jumlah dokumen (paragraf):", len(data))
