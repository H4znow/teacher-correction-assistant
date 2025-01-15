import torch
import torch_xla.core.xla_model as xm

from .model import Model
from PIL import Image, ImageFile
from transformers import TrOCRProcessor, VisionEncoderDecoderModel


class OCRModel(Model):
    def __init__(self, device: torch.device, model_path: str = "microsoft/trocr-base-handwritten"):
        super().__init__("Image2Text")
        self.device = device
        self.processor = TrOCRProcessor.from_pretrained(model_path)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_path)
        self.model = self.model.to(device=device)

    def __init_from_pytorch():
        pass

    def __init_from_onnx():
        pass

    def extract_text(self, image: ImageFile.ImageFile|list[ImageFile.ImageFile], max_tokens: int = 200):
        images = None
        if type(image) == ImageFile:
            images = [image]
        elif type(image) == list:
            images = image
        pixel_values = self.processor(images=images, return_tensors="pt").pixel_values.to(self.device)
        generated_ids = self.model.generate(pixel_values, max_new_tokens=max_tokens).to(self.device)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        return generated_text

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else xm.xla_device())

    model = OCRModel(device)
    # print(model.summary())
    # print(model.size())
    # print(model.model_name)

    # Load image
    image1 = Image.open("test/data/ocr_img_1.jpg")
    image2 = Image.open("test/data/ocr_img_2.jpg")
    result = model.extract_text([image1, image2])
    print("############ Test Results ############")
    print("\n".join(result))
    print("########## End Test Results ############")
