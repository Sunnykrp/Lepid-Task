from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import traceback
import chardet
from transformers import pipeline, BartTokenizer
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Load summarization pipeline and tokenizer
tokenizer = BartTokenizer.from_pretrained('sshleifer/distilbart-cnn-12-6')
summarizer = pipeline('summarization', model='sshleifer/distilbart-cnn-12-6')

@app.route('/')
def index():
    return "Flask API is running."

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        try:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return jsonify({'message': 'File uploaded successfully', 'fileName': filename}), 200
        except Exception as e:
            return jsonify({'message': f'Failed to upload file: {str(e)}'}), 500

@app.route('/summarize', methods=['POST'])
def summarize_file():
    data = request.get_json()
    file_name = data.get('fileName')
    if not file_name:
        return jsonify({'message': 'No file name provided'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if not os.path.exists(file_path):
        return jsonify({'message': 'File does not exist'}), 404

    try:
        document = read_file(file_path)

        # Tokenize and chunk the document
        inputs = tokenizer(document, return_tensors='pt', truncation=False)
        tokens = inputs['input_ids'][0]
        max_input_length = tokenizer.model_max_length - 50  # Adjust to account for summary length
        document_chunks = [tokens[i:i+max_input_length] for i in range(0, len(tokens), max_input_length)]

        summaries = []
        for chunk in document_chunks:
            chunk_text = tokenizer.decode(chunk, skip_special_tokens=True)
            summary = summarizer(chunk_text, max_length=150, min_length=25, do_sample=False)[0]['summary_text']
            summaries.append(summary)

        full_summary = " ".join(summaries)

        return jsonify({'summary': full_summary}), 200
    except Exception as e:
        error_message = f'Failed to summarize document: {str(e)}'
        traceback.print_exc()  # Print the full traceback to the console
        return jsonify({'message': error_message}), 500

def read_file(file_path):
    # Read a file based on its extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return read_pdf(file_path)
    elif ext == '.docx':
        return read_docx(file_path)
    elif ext == '.txt':
        return read_txt(file_path)
    else:
        raise ValueError('Unsupported file format.')

def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def read_docx(file_path):
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return '\n'.join(text)

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == "__main__":
    app.run(debug=True)
