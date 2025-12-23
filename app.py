from flask import Flask, render_template, request
from ir.search import search

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        query = request.form.get("query")
        results = search(query, top_k=3)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
