install:
	pip install --upgrade pip && \
	pip install -r requirements.txt

test:
	python -m pytest -vv test_*.py

format:
	black app/*.py

lint:
	pylint --disable=R,C app/*.py

all: install lint test