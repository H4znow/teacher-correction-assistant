import time
from rouge import Rouge  # Install with pip install rouge
from spell_checker import SpellChecker as SpellChecker1
from spell_checker2 import SpellChecker as SpellChecker2
from spell_checker3 import SpellChecker as SpellChecker3
from grammar_checker import GrammarChecker as GrammarChecker1
from grammar_checker2 import GrammarChecker as GrammarChecker2


# Example sentences with spelling errors
spelling_error_sentences = [
    "She is goinng to the libary to borrow a bok.",
    "The weather is beatiful tooday for a piknic.",
    "I recived an emale from my freind yestarday.",
    "My favorate subject in scool is mathamatics.",
    "He forgott his umbrela at home.",
    "The cat was chasing it's own tail in circls.",
    "We dicided to viset the musium this wekend.",
    "Pleese rember to bring your lunch tomorow.",
    "I tride to solve the puzzel but it was too dificult.",
    "Christmas is celbrated on decembr 25 evry ear."
]

# Example sentences with grammar errors
grammar_error_sentences = [
    "He are moving here.",
    "I am doing fine. How is you?",
    "How is they?",
    "Matt like fish",
    "Anna and Mike is going skiing",
    "I walk to the store and I bought milk.",
    "We all eat the fish and then made dessert.",
    "I will eat fish for dinner and drink milk.",
    "what be the reason for everyone leave the company.",
    "Christmas are celebrating on December 25 every year."
]

# Reference sentences for evaluation
reference_sentences = {
    "spelling": [
        "She is going to the library to borrow a book.",
        "The weather is beautiful today for a picnic.",
        "I received an email from my friend yesterday.",
        "My favorite subject in school is mathematics.",
        "He forgot his umbrella at home.",
        "The cat was chasing its own tail in circles.",
        "We decided to visit the museum this weekend.",
        "Please remember to bring your lunch tomorrow.",
        "I tried to solve the puzzle but it was too difficult.",
        "Christmas is celebrated on December 25 every year."
    ],
    "grammar": [
        "He is moving here.",
        "I am doing fine. How are you?",
        "How are they?",
        "Matt likes fish.",
        "Anna and Mike are going skiing.",
        "I walked to the store and I bought milk.",
        "We all ate the fish and then made dessert.",
        "I will eat fish for dinner and drink milk.",
        "What is the reason for everyone leaving the company?",
        "Christmas is celebrated on December 25 every year."
    ]
}


def evaluate_with_rouge(predictions, references):
    rouge = Rouge()
    scores = []
    for pred, ref in zip(predictions, references):
        score = rouge.get_scores(pred, ref, avg=True)['rouge-l']['f']
        scores.append(score)
    return scores


def time_execution_spellchecker(spell_checkers, sentences, references):
    recap = {}
    for spell_checker in spell_checkers:
        spell_checker_name = spell_checker.name()
        times = []
        predictions = []
        for sentence in sentences:
            start_time = time.time()
            corrected_text = spell_checker.correct(sentence)
            end_time = time.time()
            times.append(end_time - start_time)
            predictions.append(corrected_text)
        
        rouge_scores = evaluate_with_rouge(predictions, references)
        recap[spell_checker_name] = {
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "average_score": sum(rouge_scores) / len(rouge_scores),
        }
    return recap


def time_execution_grammar_checker(grammar_checkers, sentences, references):
    recap = {}
    for grammar_checker in grammar_checkers:
        grammar_checker_name = grammar_checker.name()
        times = []
        predictions = []
        for sentence in sentences:
            start_time = time.time()
            corrected_text = grammar_checker.correct(sentence)
            end_time = time.time()
            times.append(end_time - start_time)
            predictions.append(corrected_text)
        
        rouge_scores = evaluate_with_rouge(predictions, references)
        recap[grammar_checker_name] = {
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "average_score": sum(rouge_scores) / len(rouge_scores),
        }
    return recap


def benchmark_spellchecker():
    spell_checker1 = SpellChecker1()
    spell_checker2 = SpellChecker2()
    spell_checker3 = SpellChecker3()
    spell_checkers = [spell_checker1, spell_checker2, spell_checker3]
    recap = time_execution_spellchecker(
        spell_checkers,
        spelling_error_sentences,
        reference_sentences["spelling"]
    )
    return recap


def benchmark_grammar_checker():
    grammar_checker1 = GrammarChecker1()
    grammar_checker2 = GrammarChecker2()
    grammar_checkers = [grammar_checker1, grammar_checker2]
    recap = time_execution_grammar_checker(
        grammar_checkers,
        grammar_error_sentences,
        reference_sentences["grammar"]
    )
    return recap


recap_spell = benchmark_spellchecker()
recap_grammar = benchmark_grammar_checker()

print("Spell Checker Benchmark:")
for spell_checker, values in recap_spell.items():
    print(f"{spell_checker}:")
    print(f"  Average Time: {values['average_time']:.4f} seconds")
    print(f"  Min Time: {values['min_time']:.4f} seconds")
    print(f"  Max Time: {values['max_time']:.4f} seconds")
    print(f"  Average ROUGE-L Score: {values['average_score']:.4f}\n")

print("Grammar Checker Benchmark:")
for grammar_checker, values in recap_grammar.items():
    print(f"{grammar_checker}:")
    print(f"  Average Time: {values['average_time']:.4f} seconds")
    print(f"  Min Time: {values['min_time']:.4f} seconds")
    print(f"  Max Time: {values['max_time']:.4f} seconds")
    print(f"  Average ROUGE-L Score: {values['average_score']:.4f}\n")