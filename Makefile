MAP = maps/challenger/01_the_impossible_dream.txt

all: run

run:
	@python3 main.py $(MAP)

debug:
	python3 -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__
	rm -rf env .venv
	rm -rf .mypy_cache
	rm -rf src
	rm -rf tests

lint:
	flake8 --exclude=env .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

install:
	pip install --upgrade pip
	pip install -r requirements.txt
