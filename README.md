# TEACHER CORRECTION ASSISTANCE


# Requirements

Install requirements listed in `Pipfile` file. Using a python environnement manager (`Pipenv` for exemple) is strngly recommended:

```shell
pipenv install
```

2) Enter the environnement for executing scripts correctly : 
```shell
pipenv shell
```


# Install Spell Checker model

1) Run script to download the model locally :
```shell
py .\ai_components\download_spell_checker_model.py
```

It will add a folder in create the folder `models\t5_base_spellchecker_model` which contains the Spell Checker model

2) Try the Check speller
```shell
py .\ai_components\spell_checker.py
```


# Benchmarking

## Spell Checker Benchmark:
### T5 Spell Checker:
  Average Time: 3.8025 seconds \
  Min Time: 0.4341 seconds \
  Max Time: 31.5263 seconds \
  Average ROUGE-L Score: 0.7683 

### Bart Spell Checker:
  Average Time: 3.2829 seconds \
  Min Time: 0.8637 seconds \
  Max Time: 23.9916 seconds \
  Average ROUGE-L Score: 0.9160 

### Autocorrect Spell Checker (selected):
  Average Time: 0.0011 seconds \
  Min Time: 0.0000 seconds \
  Max Time: 0.0020 seconds \
  Average ROUGE-L Score: 0.8933 

## Grammar Checker Benchmark:
### T5 Grammar Checker (selected):
  Average Time: 3.1501 seconds \
  Min Time: 0.4146 seconds \
  Max Time: 25.4689 seconds \
  Average ROUGE-L Score: 0.9875 

### Grammar Synthesis Small:
  Average Time: 1.7816 seconds \
  Min Time: 0.5774 seconds \
  Max Time: 11.3091 seconds \
  Average ROUGE-L Score: 0.7732 
