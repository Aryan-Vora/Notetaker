from flask import Flask, render_template, request

import numpy as np
import data


def chatbot_response(msg):
    document = data.read_pdf(msg)
    return data.summarize(document)


app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)


if __name__ == "__main__":
    app.run()
