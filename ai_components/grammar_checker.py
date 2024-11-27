from transformers import T5Tokenizer, T5ForConditionalGeneration

class GrammarChecker:
    def __init__(self, model_path="./models/prithivida_grammar_error_correcter_v1"):
        # Load the locally saved model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)

    def correct(self, text):
        # Preprocess the input text
        input_text = "gec: " + text  # "gec:" is the prefix for grammar correction in this model
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")

        # Generate corrected text
        outputs = self.model.generate(input_ids, max_length=512)
        corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text

if __name__ == "__main__":
    # Initialize the grammar checker
    grammar_checker = GrammarChecker()

    # Example input text
    input_text = "She have went to the store yestarday."
    
    # Perform grammar correction
    corrected_text = grammar_checker.correct(input_text)
    print("Original:", input_text)
    print("Corrected:", corrected_text)