import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image, ImageFile


class OCRModel:
    def __init__(self, model_path="", device="cpu"):
        self.device = device
        self.processor = TrOCRProcessor.from_pretrained(model_path)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_path)
        self.model = self.model.to(device=device)

    def __init_from_pytorch():
        pass

    def __init_from_onnx():
        pass

    def extract_text(self, image, max_tokens = 200):
        images = None
        if type(image) == ImageFile:
            images = [image]
        elif type(image) == list:
            images = image
        pixel_values = self.processor(images=images, return_tensors="pt").pixel_values.to(self.device)
        generated_ids = self.model.generate(pixel_values, max_new_tokens=max_tokens).to(self.device)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        return generated_text

    def name(self):
        return "Image2Text"

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = OCRModel(model_path="microsoft/trocr-base-handwritten", device=device)

    # Load image
    image1 = Image.open("../../test/data/ocr_img_1.jpg")
    image2 = Image.open("../../test/data/ocr_img_2.jpg")
    result = model.extract_text([image1, image2])
    assert result[0] == "I like Apex and seven is good at it ."
    assert result[1] == "I like Apex and seven is good at it ."