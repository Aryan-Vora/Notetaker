# PDF Summarizer App

Welcome to the PDF Summarizer App, a web application that uses AI to summarize PDF documents. This app leverages the power of the OpenAI GPT-3.5 model to provide concise and coherent summaries of your PDF files. With this app, you can quickly extract the key information from your PDF documents in a user-friendly web interface.

## Setup Instructions

Follow these instructions to set up and run the Summarizer on your local machine.

### Prerequisites

Before you get started, make sure you have the following software and components installed on your machine:

- Python 3.6 or higher
- Pip (Python package manager)
- An OpenAI api key

### 1. Clone the Repository

You can clone this repository to your local machine using the following command if you have Git installed:

```bash
git clone https://github.com/Aryan-Vora/Notetaker.git
```

Alternatively, you can download the repository as a ZIP file and extract it to your desired location.

### 2. Set Up Your OpenAI API Key

To use the AI summarization features, you'll need to set up your OpenAI API key. If you don't already have one, you can sign up for an OpenAI account and create an API key.

Once you have your API key, set it as an environment variable. Or directly set it in data.py line 8

```bash
openai.api_key = "your_api_key_here"
```

Replace `your_api_key_here` with your actual OpenAI API key.

### 3. Install Dependencies

Navigate to the project directory and install the necessary Python dependencies using pip:

```bash
cd Notetaker
pip install -r requirements.txt
```

### 4. Run the Flask Application

Now that everything is set up, you can start the Flask application. Run the following command:

```bash
python app.py
```

or

```
flask run
```

This will start the development server, and you should see a message indicating that the app is running. By default, the app should be accessible at `http://127.0.0.1:5000/` in your web browser.

### 5. Using the App

1. Open your web browser and go to `http://127.0.0.1:5000/`.
2. Upload a PDF document that you want to summarize to the Notetaker folder
3. Enter the name of the PDF (name.pdf)
4. Click send

