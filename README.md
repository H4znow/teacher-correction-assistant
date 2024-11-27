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