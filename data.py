import fitz
import openai
from nltk.tokenize import sent_tokenize
from io import StringIO
import os
openai.api_key = os.environ["OPENAI_API_KEY"]


def open_file(filepath):
    infile = open(filepath, 'r', encoding='utf-8')
    return infile.read()


def read_pdf(filename):
    context = ""
    with fitz.open(filename) as pdf_file:
        num_pages = pdf_file.page_count
        for page_num in range(num_pages):
            page = pdf_file[page_num]
            page_text = page.get_text()
            context += page_text
    return context


def is_pdf(filename):
    return filename.endswith('.pdf')


def split_text(text, chunk_size=5000):
    chunks = []
    current_chunk = StringIO()
    current_size = 0
    sentences = sent_tokenize(text)
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


def summarize(document):
    if is_pdf(document):
        chunks = split_text(document)

        summaries = []
        for chunk in chunks:
            prompt = "Please summarize this: \n"
            summary = gpt3_completion(prompt + chunk)
            if summary.startswith("GPT-3 error:"):
                continue

            summaries.append(summary)
        return "".join(summaries)
    else:
        summary = gpt3_completion(document)
        if summary.startswith("GPT-3 error:"):
            return summary + "Sorry my developer couldn't pay the GPT-3 bill."
        return summary
