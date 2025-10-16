# 🔐 Elastic Auto Parser

**Elastic Auto Parser** is an automated log normalization and indexing framework that maps heterogeneous log sources to the **Elastic Common Schema (ECS)** using **Python**, **Logstash**, and **Docker**.  
It automatically detects log types, normalizes events, and assigns them to the correct **Elasticsearch index** based on a configurable taxonomy.

---

## 🧠 Purpose

Provide a reproducible and extensible pipeline for **log normalization and dynamic index routing** in SIEM environments.

- Detect log source and category automatically  
- Map raw events to ECS-compliant fields  
- Route events to the correct Elasticsearch index using a lookup taxonomy  
- Enable structured, compliant, and scalable search across multiple data sources  

---

## 🧩 Technology Stack

| Component | Role |
|------------|------|
| **Python 3.11** | Pattern detection, ECS mapping, and metadata enrichment |
| **Logstash** | Data ingestion, taxonomy lookup, and dynamic index routing |
| **Elasticsearch + Kibana** | Storage and visualization |
| **Docker Compose** | Environment orchestration |
| **NDJSON** | Intermediate event format |

---

## 🧱 Index Taxonomy

Elastic Auto Parser supports a **taxonomy-driven indexing strategy** that associates each data source with a specific index name.

### Example structure

```
logs-<domain>-<vendor>-<product>-<source>-<env>-<region>
```

### Example entries (`config/taxonomy/index_taxonomy_en.json`)

```json
{
  "cisco|asa|syslog": "logs-security-cisco-asa-syslog-prod-eu",
  "apache|httpd|access": "logs-web-apache-httpd-access-dev-eu"
}
```

This JSON acts as a **lookup table** for Logstash or the Python parser.  
When a new event is parsed, its vendor, product, and source are matched to the correct index.

---

## ⚙️ How It Works

1. **Python parser** detects the log type and normalizes fields to ECS.  
2. It generates metadata for Logstash:  
   ```json
   {
     "@metadata": {
       "lookup_key": "vendor|product|source"
     },
     "event": {
       "vendor": "apache",
       "product": "httpd",
       "category": "access"
     }
   }
   ```
3. **Logstash** reads this metadata, uses `translate` with  
   `config/taxonomy/index_taxonomy_en.json` to resolve the final index name.  
4. If no match is found, a **fallback convention** builds an index name automatically.

---

## 🚀 Quick Start

```bash
# 1. Start Elastic, Kibana, and Logstash
docker compose up -d

# 2. (Optional) Activate Python virtual environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Run the parser to normalize raw logs
python src/parser/main.py --in data/raw --out data/out/parsed.ndjson

# 4. Logstash automatically picks up NDJSON and pushes to Elasticsearch
# Verify new indices in Kibana → http://localhost:5601
```

---

## 🧩 Logstash Integration

### Mount taxonomy in `docker-compose.yml`

```yaml
services:
  logstash:
    volumes:
      - ./config/logstash/pipeline.conf:/usr/share/logstash/pipeline/logstash.conf:ro
      - ./config/taxonomy/index_taxonomy_en.json:/usr/share/logstash/pipeline/index_taxonomy_en.json:ro
      - ./data/out:/data/out
```

### Pipeline logic (`config/logstash/pipeline.conf`)

```conf
filter {
  mutate {
    lowercase => ["[event][vendor]", "[event][product]", "[event][category]"]
    gsub => [
      "[event][vendor]",  "\s+", "-",
      "[event][product]", "\s+", "-",
      "[event][category]","\s+", "-"
    ]
  }

  mutate {
    add_field => {
      "[@metadata][lookup_key]" => "%{[event][vendor]}|%{[event][product]}|%{[event][category]}"
    }
  }

  translate {
    field            => "[@metadata][lookup_key]"
    destination      => "[@metadata][target_index]"
    dictionary_path  => "/usr/share/logstash/pipeline/index_taxonomy_en.json"
    exact            => true
    fallback         => ""
  }

  if [@metadata][target_index] == "" {
    ruby {
      code => '
        def part(v); v.nil? || v.empty? ? nil : v end
        parts = ["logs", event.get("[event][vendor]"), event.get("[event][product]"), event.get("[event][category]")].map{|x| part(x)}.compact
        event.set("[@metadata][target_index]", parts.join("-"))
      '
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "%{[@metadata][target_index]}"
  }
}
```

---

## 🧩 Parser Metadata Example (Python)

```python
def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "-").replace("/", "-").replace("_", "-")

event.setdefault("event", {})
event.setdefault("@metadata", {})

vendor  = _norm(detected_vendor)
product = _norm(detected_product)
source  = _norm(detected_category)

event["event"]["vendor"]   = vendor
event["event"]["product"]  = product
event["event"]["category"] = source
event["@metadata"]["lookup_key"] = f"{vendor}|{product}|{source}"
```

---

## 🛠️ Makefile Shortcuts

```bash
make up        # Start all Docker services
make down      # Stop and remove containers
make parse     # Run parser locally
make logs      # View Logstash logs
```

---

## 📊 View in Kibana

- **URL:** [http://localhost:5601](http://localhost:5601)  
- Create a **Data View** for `logs-*`  
- Explore ECS fields grouped by source and category.

---

## 📘 License

Licensed under the [MIT License](LICENSE).

---

### 🧭 Style Guide Compliance (Bishop Fox V2.0)

- Active voice and clear subject–action order  
- Consistent capitalization for headings and acronyms  
- Inline code for commands, paths, and fields  
- Objective, technical tone (no first-person)  
- Focused on clarity, reproducibility, and professionalism  

---

**Maintainer:** [**Ricardo Rivera Aguilera**](https://github.com/rickardo1991)  
**Repository:** [github.com/rickardo1991/elastic-parser](https://github.com/rickardo1991/elastic-parser)
