from flask import Flask, request, render_template, jsonify, url_for
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)
app = Flask(__name__)


def preprocess_image(image_path):
    # Placeholder: Preprocess the image and return the preprocessed image path and list of image paths for lines
    processed_image = "static/images/processed/preprocessed_image.png"

    # Directory where line images are stored
    line_images_dir = "static/images/processed/lines"
    os.makedirs(line_images_dir, exist_ok=True)

    # Example: Assuming images are already created or you process them here
    # Get all image files from the directory
    lines_images = [os.path.join(line_images_dir, filename) for filename in os.listdir(line_images_dir) if
                    filename.endswith('.png')]

    return processed_image, lines_images

def extract_text(lines):
    # Placeholder: Extract text from lines
    return "Extracted text from lines."

def syntax_check(text):
    # Placeholder: Perform syntax check and return two versions of the text
    return text, text + " (syntactically fixed)"

def grammar_check(text):
    # Placeholder: Perform grammar check and return two versions of the text
    return text, text + " (grammatically fixed)"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-image-quality', methods=['POST'])
def check_image_quality():
    # Handle user decision on image quality
    decision = request.json.get('decision')
    if decision == 'yes':
        image_path = "static/images/uploaded_image.jpg"  # Example image path
        preprocessed_image, lines = preprocess_image(image_path)
        # {{url_for('static', preprocessed_image)}}
        return jsonify({"status": "preprocessed", "image": preprocessed_image, "lines": lines})
    return jsonify({"status": "redo"})

@app.route('/check-preprocessing', methods=['POST'])
def check_preprocessing():
    decision = request.json.get('decision')
    if decision == 'yes':
        lines = request.json.get('lines')
        extracted_text = extract_text(lines)
        return jsonify({"status": "text_extracted", "text": extracted_text})
    return jsonify({"status": "redo"})

@app.route('/check-syntax', methods=['POST'])
def check_syntax():
    text = request.json.get('text')
    syntax_fixed, fixed_version = syntax_check(text)
    return jsonify({"original": syntax_fixed, "fixed": fixed_version})

@app.route('/check-grammar', methods=['POST'])
def check_grammar():
    text = request.json.get('text')
    grammar_fixed, fixed_version = grammar_check(text)
    return jsonify({"original": grammar_fixed, "fixed": fixed_version})

if __name__ == '__main__':
    app.run(debug=True)