from flask import Flask, render_template, request, redirect, send_file
from ir.search import search
import os
import sys
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# CONFIG
# =========================
PDF_FOLDER = "dataset/jurnal"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(PDF_FOLDER, exist_ok=True)

# =========================
# HELPER
# =========================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def run_pipeline():
    """
    WAJIB pakai python yang sama dengan Flask
    """
    python = sys.executable
    os.system(f'"{python}" ir/pdf_reader.py')
    os.system(f'"{python}" ir/preprocessing.py')
    os.system(f'"{python}" ir/indexing.py')


# =========================
# ROUTE: SEARCH
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query", "")
        if query.strip():
            results = search(query, top_k=3)

    return render_template(
        "index.html",
        results=results,
        query=query
    )


# =========================
# ROUTE: MANAGE PDF
# =========================
@app.route("/manage-pdf")
def manage_pdf():
    files = sorted(os.listdir(PDF_FOLDER))
    return render_template("manage_pdf.html", files=files)


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

        # 🔥 AUTO PIPELINE (FIX)
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

        # 🔥 AUTO PIPELINE (FIX)
        run_pipeline()

    return redirect("/manage-pdf")


# =========================
# ROUTE: VIEW
# =========================
@app.route("/view-pdf")
def view_pdf():
    filename = request.args.get("file")
    if not filename:
        return "File not found", 404

    path = os.path.join(PDF_FOLDER, filename)
    if not os.path.exists(path):
        return "File not found", 404

    return send_file(
        path,
        mimetype="application/pdf",
        as_attachment=False
    )


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
