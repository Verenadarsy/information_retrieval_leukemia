from flask import Flask, render_template, request, redirect, send_file
from ir.search import search
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

PDF_FOLDER = "dataset/jurnal"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(PDF_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""   # 🔥 FIX ERROR KAMU (biar GET ga error)

    if request.method == "POST":
        query = request.form.get("query")
        if query:
            results = search(query, top_k=3)

    return render_template(
        "index.html",
        results=results,
        query=query
    )


@app.route("/manage-pdf")
def manage_pdf():
    files = os.listdir(PDF_FOLDER)
    return render_template("manage_pdf.html", files=files)


@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    if "pdf" not in request.files:
        return redirect("/manage-pdf")

    file = request.files["pdf"]

    if file.filename == "":
        return redirect("/manage-pdf")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(PDF_FOLDER, filename)
        file.save(save_path)

        # AUTO PIPELINE
        os.system("python ir/pdf_reader.py")
        os.system("python ir/preprocessing.py")
        os.system("python ir/indexing.py")

    return redirect("/manage-pdf")


@app.route("/delete-pdf/<filename>", methods=["POST"])
def delete_pdf(filename):
    path = os.path.join(PDF_FOLDER, filename)

    if os.path.exists(path):
        os.remove(path)

        # AUTO PIPELINE
        os.system("python ir/pdf_reader.py")
        os.system("python ir/preprocessing.py")
        os.system("python ir/indexing.py")

    return redirect("/manage-pdf")


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


if __name__ == "__main__":
    app.run(debug=True)
