import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import requests

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load image
image1 = Image.open("photo_2024-11-20_11-45-22.jpg")

image1.save("test2.jpg")


image2 = Image.open("photo_2024-11-20_11-42-39.jpg")
image2.save("test3.jpg")

images = [image1, image2]

# Load processor and model
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-handwritten').to(device)

# Prepare pixel values and move to the correct device
pixel_values = processor(images=images, return_tensors="pt").pixel_values.to(device)

# Generate text
generated_ids = model.generate(pixel_values, max_new_tokens=200)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)
print(generated_text)
