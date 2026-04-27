MAP = maps/easy/01_linear_path.txt

# install:
# 	pip install -r requirements.txt

run:
	@python3 main.py

debug:
	python3 -m pdb main.py $(MAP)

clean:
	rm -rf __pycache__
	rm -rf env .venv
	rm -rf .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	numpy . --strict
