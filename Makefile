up:
	docker compose up -d

down:
	docker compose down -v

parse:
	python src/parser/main.py --in data/raw --out data/out/parsed.ndjson

reset:
	rm -f data/out/parsed.ndjson
