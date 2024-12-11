import argparse
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import os

# Set device
def get_device():
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")  # For Apple Silicon devices
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")
    return device

def load_images_from_directory(directory):
    """
    Load all image files from the specified directory into a list of PIL Image objects.

    Args:
        directory (str): The path to the directory containing image files.

    Returns:
        list: A list of PIL Image objects.
    """
    supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif")  # Add more formats as needed
    images = []

    # Iterate through all files in the directory
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        # Check if the file is an image based on its extension
        if file_name.lower().endswith(supported_formats):
            try:
                # Load the image and append it to the list
                image = Image.open(file_path)
                images.append(image)
                print(f"Loaded image: {file_path}")
            except Exception as e:
                print(f"Failed to load image: {file_path}. Error: {e}")

    return images

def main():
    parser = argparse.ArgumentParser(description="Process images for text recognition.")
    parser.add_argument("--image_dir", type=str, required=True, help="Path to the directory containing image files.")
    parser.add_argument("--model_name", type=str, required=True, help="Name of the model to load.")
    args = parser.parse_args()

    # Load images from the specified directory
    images = load_images_from_directory(args.image_dir)

    # Get device
    device = get_device()

    # Load processor and model
    processor = TrOCRProcessor.from_pretrained(args.model_name)
    model = VisionEncoderDecoderModel.from_pretrained(args.model_name).to(device)

    # Prepare pixel values and move to the correct device
    pixel_values = processor(images=images, return_tensors="pt").pixel_values.to(device)

    # Generate text
    generated_ids = model.generate(pixel_values, max_new_tokens=2000)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
    print("Generated text:", generated_text)

if __name__ == "__main__":
    main()

# Example of usage: python image2text_recognition.py --image_dir output_crop/cropped --model_name microsoft/trocr-base-handwritten