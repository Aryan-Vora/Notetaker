import time
import fitz
import openai
from nltk.tokenize import sent_tokenize
from io import StringIO
import os
from fpdf import FPDF
openai.api_key = os.environ["OPENAI_API_KEY"]


def open_file(filepath):
    infile = open(filepath, 'r', encoding='utf-8')
    return infile.read()


def read_pdf(filename):
    context = []  # Initialize an empty list to store page text
    with fitz.open(filename) as pdf_file:
        num_pages = pdf_file.page_count
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


def gpt3_completion(prompt, model='gpt-3.5-turbo', temp=0.5, top_p=0.3, tokens=1000):
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
    # Add a page
    pdf.add_page()
    # set title
    pdf.set_title("Summary")
    # set style and size of font for the title (bigger font)
    pdf.set_font("Arial", size=25)
    # open the text file in read mode
    with open(textfile, "r") as f:
        # insert the title
        pdf.cell(0, 10, "Summary", ln=True, align='C')
        # reset the font size to the original size
        pdf.set_font("Arial", size=15)
        # insert the texts in pdf
        for x in f:
            pdf.multi_cell(0, 10, x, align='L')
    # save the pdf with name .pdf
    pdf.output("output.pdf")

# Call this function before the `summarize` function to check its behavior
# convert_to_pdf("output.txt")


def summarize(document):
    f = open("output.txt", "w")
    if is_pdf(document):
        chunks = split_text(document)

        summaries = []
        for chunk in chunks:
            prompt = "Please take notes on this. They should be in paragraph form and only include the most important details. It is fine if it is short."
            summary = gpt3_completion(prompt + chunk)
            if summary.startswith("GPT-3 error:"):
                continue

            summaries.append(summary)
            print(summary)
            f.write(summary + "\n\n")
            time.sleep(1)  # Add a 1-second delay between chunks
        f.close()
        convert_to_pdf("output.txt")
        return "\n".join(summaries)
    else:
        summary = gpt3_completion(document)
        f.close()
        convert_to_pdf("output.txt")
        if summary.startswith("GPT-3 error:"):
            return summary + " Sorry, my developer couldn't pay the GPT-3 bill."
        return summary
