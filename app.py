from flask import Flask, render_template, request, jsonify, Response
import data
import os
from uuid import uuid4

app = Flask(__name__)
app.static_folder = 'static'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def chatbot_response(msg):
    if msg.endswith('.pdf'):
        document = data.read_pdf(msg)
    else:
        document = msg
    return data.summarize(document)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)


@app.route("/upload", methods=["POST"])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file and file.filename.endswith('.pdf'):
        filename = f"{uuid4()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        document = data.read_pdf(filepath)

        def generate():
            for summary in data.summarize(document):
                yield summary + "\n"
        return Response(generate(), mimetype='text/plain')
    return jsonify({"error": "Invalid file type"})


if __name__ == "__main__":
    app.run()
