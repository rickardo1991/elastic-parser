# 🔐 Elastic Auto Parser

**Auto-normalización de logs a ECS** con Python + Logstash + Docker.
Detecta el tipo de log (Apache, Syslog, etc.), **mapea a Elastic Common Schema (ECS)** y lo envía a Elasticsearch para visualizar en Kibana.

## 🧠 Objetivo
Demostrar un pipeline reproducible de parsing y normalización orientado a SIEM:
- **Detección automática** del tipo de fuente.
- **Mapeo a ECS** mediante reglas declarativas (YAML).
- **Entrega a Elasticsearch** vía Logstash.

## 🧩 Stack
- ElasticSearch + Kibana (Docker)
- Logstash (ingesta)
- Python 3.11 (detección y mapeo a ECS)
- NDJSON como formato intermedio

## 🚀 Quick start

```bash
# 1) Arrancar Elastic, Kibana y Logstash
docker compose up -d

# 2) Crear el entorno Python local (opcional si usarás solo Docker)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3) Ejecutar el parser sobre data/raw y generar NDJSON ECS en data/out
python src/parser/main.py --in data/raw --out data/out/parsed.ndjson

# 4) Hacer que Logstash lea el NDJSON y lo envíe a Elasticsearch
# (Logstash ya está leyendo data/out/parsed.ndjson por volumen compartido)
# Espera unos segundos y verifica el índice en Kibana (http://localhost:5601)
```

## 📊 Ver en Kibana
- URL: `http://localhost:5601`
- Crea un Data View para `ecs-auto-*` y explora los campos ECS.

## 🏗️ Estructura
- `src/parser`: detección por patrones → mapeo ECS → export NDJSON
- `config/parser/config.yaml`: reglas declarativas de mapeo
- `config/logstash/pipeline.conf`: input NDJSON → output Elasticsearch

## 🛠️ Makefile (atajos)
```bash
make up        # docker compose up -d
make down      # docker compose down -v
make parse     # corre el parser local
make reset     # borra datos del volumen
```

## 🤝 Contribuir
PRs bienvenidos: nuevas detecciones, mappings ECS o fuentes de log.

## 📜 Licencia
MIT
