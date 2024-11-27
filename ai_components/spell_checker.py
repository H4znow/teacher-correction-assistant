from transformers import T5Tokenizer, T5ForConditionalGeneration

class SpellChecker:
    def __init__(self, local_path):
        self.tokenizer = T5Tokenizer.from_pretrained(local_path)
        self.model = T5ForConditionalGeneration.from_pretrained(local_path)

    def correct(self, input_text):
        # Preprocess the input text
        input_ids = self.tokenizer("spellcheck: " + input_text, return_tensors="pt").input_ids
        
        # Generate corrected text
        outputs = self.model.generate(input_ids)
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text

if __name__ == "__main__":
    # Path to the locally saved model
    local_model_path = "./models/t5_base_spellchecker_model"

    # Initialize the SpellChecker class
    spell_checker = SpellChecker(local_model_path)

    # Example input text
    input_text = "christmas is celbrated on decembr 25 evry ear"
    
    # Correct the text
    corrected_text = spell_checker.correct(input_text)
    print("#" * 95, "\nCorrected text:", corrected_text)