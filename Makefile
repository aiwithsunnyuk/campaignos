install:
	pip install -r requirements.txt

data:
	python scripts/generate_data.py

run:
	streamlit run app/Home.py

test:
	pytest -q

docker:
	docker compose up --build
