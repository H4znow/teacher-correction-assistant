import torch
import torch_xla.core.xla_model as xm

from lib.ocr_model import OCRModel
from lib.grammar_checker import GrammarChecker
from lib.spell_checker import SpellChecker
from PIL import Image


def load_images():
    # TODO: get the image here
    # I used fake images for test
    image1 = Image.open("./test/data/ocr_img_1.jpg")
    image2 = Image.open("./test/data/ocr_img_2.jpg")
    return [image1, image2]

def image2text(images, device: torch.device):
    # TODO: Replace path with the quantized path
    ocr_model_path = "microsoft/trocr-base-handwritten"
    model = OCRModel(device, model_path = ocr_model_path)
    return model.extract_text(images)

def check_first_step(device: torch.device):
    img = load_images()
    result = image2text(img, device=device)
    print("Here is the transcription of the text in the image provided: ")
    print("\n".join(result))

    answer = input("Is it ok ?: y(es) or n(o): ")
    answer = answer.strip().lower()
    return result, answer


device = torch.device("cuda" if torch.cuda.is_available() else xm.xla_device())
# TODO: Replace by the path to the quantized models
spell_checker_path = "Bhuvana/t5-base-spellchecker"
# TODO: Replace by the path to the quantized models
grammar_checker_path = "prithivida/grammar_error_correcter_v1"

extracted_text, answer = check_first_step(device=device)
while answer == "n":
    extracted_text, answer = check_first_step(device=device)

spell_checker = SpellChecker(device, model_path=spell_checker_path)
grammar_checker = GrammarChecker(device, model_path=grammar_checker_path)
result = []

# Correct spelling and grammar errors
for line in extracted_text:
    spell_output = spell_checker.correct(line)
    correct_sent = grammar_checker.correct(spell_output)
    result.append(correct_sent)

print("\n".join(result))
