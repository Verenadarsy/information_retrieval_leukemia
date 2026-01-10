from flask import Flask, render_template, request, redirect, send_file
from ir.search import search
import os
import sys
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# CONFIG
# =========================
PDF_FOLDER = "dataset/jurnal"
PROCESSED_FOLDER = "processed"
INDEX_FOLDER = "index"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(INDEX_FOLDER, exist_ok=True)

# =========================
# HELPER
# =========================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def run_pipeline():
    """
    Run indexing pipeline - sesuai dengan struktur file kamu
    """
    python = sys.executable
    # Pastikan script-script ini ada di folder ir/
    os.system(f'"{python}" ir/pdf_reader.py')
    os.system(f'"{python}" ir/preprocessing.py')
    os.system(f'"{python}" ir/indexing.py')

def get_pdf_files():
    """Get list of PDF files"""
    return [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')]

def get_pdf_filename_from_jurnal(jurnal_name):
    """Convert jurnal name to PDF filename"""
    # Jika jurnal sudah berupa nama file PDF
    if jurnal_name.lower().endswith('.pdf'):
        return jurnal_name

    # Coba cari PDF dengan nama yang mirip
    pdf_files = get_pdf_files()
    for pdf in pdf_files:
        # Cek apakah nama file mengandung nama jurnal
        if jurnal_name.lower() in pdf.lower():
            return pdf

    # Jika tidak ditemukan, return yang pertama
    return pdf_files[0] if pdf_files else None

def get_total_paragraphs():
    """
    Hitung total paragraf hasil processing
    """
    path = os.path.join(PROCESSED_FOLDER, "paragraphs.json")
    if not os.path.exists(path):
        return 0

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return len(data)



# =========================
# ROUTE: SEARCH
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""
    error = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            try:
                # Get search results - remove limit
                search_results = search(query, top_k=50)

                # Enrich results with PDF information
                for i, result in enumerate(search_results):
                    result['rank'] = i + 1

                    # Get PDF filename from jurnal field
                    jurnal_name = result.get('jurnal', '')
                    if jurnal_name:
                        pdf_filename = get_pdf_filename_from_jurnal(jurnal_name)
                        result['pdf_filename'] = pdf_filename
                        result['view_url'] = f"/pdf/{pdf_filename}" if pdf_filename else "#"
                    else:
                        result['pdf_filename'] = "Unknown"
                        result['view_url'] = "#"

                results = search_results

            except Exception as e:
                error = f"Search error: {str(e)}"
                print(f"Search error: {e}")

    papers_count = len(get_pdf_files())

    return render_template(
        "index.html",
        results=results,
        query=query,
        papers_count=papers_count,
        error=error
    )

# =========================
# ROUTE: MANAGE PDF
# =========================
@app.route("/manage-pdf")
def manage_pdf():
    files = get_pdf_files()
    total_paragraphs = get_total_paragraphs()
    return render_template("manage_pdf.html", files=files, total_paragraphs=total_paragraphs)



# =========================
# ROUTE: UPLOAD
# =========================
@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    if "pdf" not in request.files:
        return redirect("/manage-pdf")

    file = request.files["pdf"]

    if file.filename == "":
        return redirect("/manage-pdf")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(PDF_FOLDER, filename))
        run_pipeline()

    return redirect("/manage-pdf")

# =========================
# ROUTE: DELETE
# =========================
@app.route("/delete-pdf/<filename>", methods=["POST"])
def delete_pdf(filename):
    path = os.path.join(PDF_FOLDER, filename)

    if os.path.exists(path):
        os.remove(path)
        run_pipeline()

    return redirect("/manage-pdf")

# =========================
# ROUTE: VIEW PDF
# =========================
@app.route("/pdf/<filename>")
def view_pdf(filename):
    """Simple PDF viewer"""
    filename = secure_filename(filename)
    path = os.path.join(PDF_FOLDER, filename)

    if not os.path.exists(path):
        return "File not found", 404

    return send_file(
        path,
        mimetype="application/pdf",
        as_attachment=False
    )

# =========================
# ROUTE: REINDEX
# =========================
@app.route("/reindex", methods=["POST"])
def reindex():
    """Manual reindexing"""
    run_pipeline()
    return redirect("/manage-pdf")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("Starting Leukemia Research IR System...")
    print(f"PDF folder: {PDF_FOLDER}")
    print(f"PDF files: {len(get_pdf_files())}")

    app.run(debug=True, port=5000)