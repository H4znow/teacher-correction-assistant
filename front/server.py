import shutil

import torch
from flask import Flask, request, render_template, jsonify
import os

from lib.image2text_recognition import load_images_from_directory, OCRModel, process_batch
from lib.preprocess_image import remove_background, crop_lines

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)
app = Flask(__name__)
device = torch.device("cpu")

def clean_lines_dir(directory_path = "../front/static/images/processed/lines"):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        shutil.rmtree(directory_path)

def preprocess_image(image_path, image_name):
    # Placeholder: Preprocess the image and return the preprocessed image path and list of image paths for lines
    processed_image = "static/images/processed/preprocessed_image.png"
    # Directory where line images are stored
    line_images_dir = "static/images/processed/lines"
    # os.makedirs(line_images_dir, exist_ok=True)

    image = remove_background(image_path, image_name, "../front/static/images/processed", "preprocessed_image.png")

    crop_lines(image, "../front/static/images/processed/lines")

    # Example: Assuming images are already created or you process them here
    # Get all image files from the directory
    lines_images = [os.path.join(line_images_dir, filename) for filename in os.listdir("../front/static/images/processed/lines") if
                    filename.endswith('.png')]

    return processed_image, lines_images

def extract_text(lines):

    lines_dir = "../front/static/images/processed/lines"

    images = load_images_from_directory(lines_dir)

    model = OCRModel(device)

    # Process images in batches
    generated_text = process_batch(images, model)

    return generated_text

def syntax_check(text):
    # Placeholder: Perform syntax check and return two versions of the text
    return text, text + " (syntactically fixed)"

def grammar_check(text):
    # Placeholder: Perform grammar check and return two versions of the text
    return text, text + " (grammatically fixed)"

def verify_and_set_device(device_selected_text):
    global device
    if device_selected_text == "cuda":
        if not torch.cuda.is_available():
            return False, "GPU is unavailable on your device!"
        device = torch.device("cuda")
    elif device_selected_text == "tpu":
        try:
            import torch_xla.core.xla_model as xm
            # Check if TPU device is accessible
            device = xm.xla_device()  # This will succeed if XLA is available
        except ImportError:
            return False, "TPU is unavailable on your device!"
    elif device_selected_text == "mps":
        if not torch.backends.mps.is_available():
            return False, "Metal is unavailable on your device!"
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    return True, "OK"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-image-quality', methods=['POST'])
def check_image_quality():
    # Handle user decision on image quality
    decision = request.json.get('decision')
    if decision == 'yes':
        image_path = "../front/static/images"  # Example image path
        preprocessed_image, lines = preprocess_image(image_path, "uploaded_image.jpg")
        # {{url_for('static', preprocessed_image)}}
        return jsonify({"status": "preprocessed", "image": preprocessed_image, "lines": lines})
    return jsonify({"status": "redo"})

@app.route('/extract-text', methods=['POST'])
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

@app.route('/set-device', methods=['POST'])
def set_device():
    selected_device_text = request.json.get('device')

    status, reason = verify_and_set_device(selected_device_text)

    print(selected_device_text)

    print(device.type)

    return jsonify({"status": status, "device": selected_device_text, "reason": reason})

@app.route('/check-grammar', methods=['POST'])
def check_grammar():
    text = request.json.get('text')
    grammar_fixed, fixed_version = grammar_check(text)
    return jsonify({"original": grammar_fixed, "fixed": fixed_version})

if __name__ == '__main__':
    app.run(debug=True)