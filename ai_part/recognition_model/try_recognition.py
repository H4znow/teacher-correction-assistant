import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import os

from ai_part.recognition_model.preprocess_image import ROOT_DIR

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# image1 = Image.open("photo_2024-11-20_11-45-22.jpg")
# image1 = Image.open("./output/output_image2.png")
# # image1 = cv2.imread("test1.jpg")
#
# # image1.save("test2.jpg")
#
#
# image2 = Image.open("photo_2024-11-20_11-42-39.jpg")
# image2.save("test3.jpg")

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

images = load_images_from_directory(os.path.join(ROOT_DIR, "output_crop/croppep6"))

# Load processor and model
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten').to(device)

# Prepare pixel values and move to the correct device
pixel_values = processor(images=images, return_tensors="pt").pixel_values.to(device)

# Generate text
generated_ids = model.generate(pixel_values, max_new_tokens=2000)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
print(generated_text)
