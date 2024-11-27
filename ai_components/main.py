# App script for the AI components
from spell_checker import SpellChecker
from grammar_checker import GrammarChecker

def main():
    # Initialize verbose mode
    verbose = True

    # Input sentence
    input_sentence = input("Enter a sentence to correct spelling and grammar: ")

    # Verbose output: original sentence
    if verbose:
        print("\nStep 1: Input Sentence")
        print(f"Original Sentence: {input_sentence}")

    # Step 2: Spelling Correction
    spell_checker = SpellChecker()  # Path to your spell-check model
    corrected_spelling = spell_checker.correct(input_sentence)

    # Verbose output: after spelling correction
    if verbose:
        print("\nStep 2: Spelling Correction")
        print(f"Corrected Spelling: {corrected_spelling}")

    # Step 3: Grammar Correction
    grammar_checker = GrammarChecker()  # Path to your grammar-check model
    corrected_grammar = grammar_checker.correct(corrected_spelling)

    # Verbose output: after grammar correction
    if verbose:
        print("\nStep 3: Grammar Correction")
        print(f"Corrected Grammar: {corrected_grammar}")

    # Final Output
    print("\nFinal Corrected Sentence:")
    print(corrected_grammar)

if __name__ == "__main__":
    main()