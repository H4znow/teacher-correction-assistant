import argparse
import json
import torch
from torch.xpu import device
from transformers import TrOCRProcessor
from PIL import Image
import os
from transformers import VisionEncoderDecoderModel
import logging

from ai_part.recognition_model.utils import get_device

logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

def load_images_from_directory(directory):
    supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif")
    images = []

    # Iterate through all files in the directory
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)

        if file_name.lower().endswith(supported_formats):
            try:
                image = Image.open(file_path).convert("RGB")
                images.append(image)
                # print(f"Loaded image: {file_path}")
            except Exception as e:
                print(f"Failed to load image: {file_path}. Error: {e}")

    return images

def process_batch(images, processor, model, device, batch_size):
    # Split the images into smaller batches to avoid OOM errors
    batch_texts = []
    for i in range(0, len(images), batch_size):
        batch_images = images[i:i + batch_size]

        # Prepare pixel values and move to the correct device
        pixel_values = processor(images=batch_images, return_tensors="pt").pixel_values.to(device)

        # Generate text
        generated_ids = model.generate(pixel_values, max_new_tokens=2000)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
        batch_texts.extend(generated_text)

    return batch_texts

def main():
    parser = argparse.ArgumentParser(description="Process images for text recognition.")
    parser.add_argument("--image_dir", type=str, required=True, help="Path to the directory containing image files.")
    parser.add_argument("--model_name", type=str, required=True, help="Name of the model to load.")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size of images to fit into the model.")
    parser.add_argument("--device",  type=str, required=False,
                        help="The device to be used for benchmark.")
    args = parser.parse_args()

    # Load images from the specified directory
    images = load_images_from_directory(args.image_dir)

    # Get device
    if args.device is None:
        device = get_device()
    else:
        device = torch.device(args.device)
    # Load processor and model
    processor = TrOCRProcessor.from_pretrained(args.model_name)

    model = VisionEncoderDecoderModel.from_pretrained(
        args.model_name,
    ).to(device)

    # Process images in batches
    generated_text = process_batch(images, processor, model, device, args.batch_size)

    print(json.dumps(generated_text, ensure_ascii=False, indent=2))  # JSON formatted output
    return generated_text

if __name__ == "__main__":
    main()
