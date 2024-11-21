import time
import fitz  # PyMuPDF
import openai
import logging
from nltk.tokenize import sent_tokenize
from io import StringIO
import os
from fpdf import FPDF

openai.api_key = os.environ["OPENAI_API_KEY"]

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def open_file(filepath):
    infile = open(filepath, 'r', encoding='utf-8')
    return infile.read()


def read_pdf(filename):
    logging.info(f"Reading PDF file: {filename}")
    context = []  # Initialize an empty list to store page text
    try:
        pdf_file = fitz.open(filename)
    except Exception as e:
        logging.error(f"Error opening PDF file: {e}")
        return []

    num_pages = pdf_file.page_count
    logging.info(f"Number of pages in PDF: {num_pages}")
    page_num = 0
    while page_num < num_pages:
        # Read up to 5 pages or remaining pages
        pages_to_read = min(5, num_pages - page_num)
        page_texts = []
        for _ in range(pages_to_read):
            page = pdf_file[page_num]
            page_text = page.get_text()
            page_texts.append(page_text)
            page_num += 1
        # Combine page texts into one string and add to the list
        context.append(''.join(page_texts))
        logging.info(
            f"Read pages {page_num - pages_to_read + 1} to {page_num}")
    pdf_file.close()
    return context


def is_pdf(filenames):
    return [filename.endswith('.pdf') for filename in filenames]


def split_text(sentences, chunk_size=5000):
    chunks = []
    current_chunk = StringIO()
    current_size = 0
    for sentence in sentences:
        sentence_size = len(sentence)
        if sentence_size > chunk_size:
            while sentence_size > chunk_size:
                chunk = sentence[:chunk_size]
                chunks.append(chunk)
                sentence = sentence[chunk_size:]
                sentence_size -= chunk_size
                current_chunk = StringIO()
                current_size = 0
        if current_size + sentence_size < chunk_size:
            current_chunk.write(sentence)
            current_size += sentence_size
        else:
            chunks.append(current_chunk.getvalue())
            current_chunk = StringIO()
            current_chunk.write(sentence)
            current_size = sentence_size
    if current_chunk:
        chunks.append(current_chunk.getvalue())
    return chunks


def gpt3_completion(prompt, model='gpt-3.5-turbo', temp=0.5, top_p=0.3, tokens=200):
    prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}],
            temperature=temp,
            top_p=top_p,
            max_tokens=tokens
        )
        return response.choices[0].message.content
    except Exception as oops:
        return "GPT-3 error: %s" % oops


def convert_to_pdf(textfile):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_title("Summary")
    pdf.set_font("Arial", size=25)
    with open(textfile, "r") as f:
        pdf.cell(0, 10, "Summary", ln=True, align='C')
        pdf.set_font("Arial", size=15)
        for x in f:
            pdf.multi_cell(0, 10, x, align='L')
    pdf.output("output.pdf")


def summarize(document):
    if isinstance(document, list):  # Check if document is a list (PDF content)
        chunks = split_text(document)
        for chunk in chunks:
            prompt = "Please take notes on this. They should be in paragraph form and only include the most important details. It is fine if it is short."
            summary = gpt3_completion(prompt + chunk)
            if summary.startswith("GPT-3 error:"):
                continue
            yield summary
            time.sleep(1)  # Add a 1-second delay between chunks
    else:
        summary = gpt3_completion(document)
        if summary.startswith("GPT-3 error:"):
            yield summary + " Sorry, my developer couldn't pay the GPT-3 bill."
        else:
            yield summary
