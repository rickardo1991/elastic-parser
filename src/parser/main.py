import argparse
import json
from pathlib import Path
import yaml
from src.parser.detectors import Detector, guess_type
from src.parser.ecs_mapper import apache_to_ecs, syslog_to_ecs

def load_config(path: Path):
    with path.open() as f:
        return yaml.safe_load(f)

def parse_line(log_type: str, line: str) -> dict:
    if log_type == "apache_access":
        return apache_to_ecs(line)
    if log_type == "syslog":
        return syslog_to_ecs(line)
    return {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Dir con logs crudos")
    ap.add_argument("--out", dest="out", required=True, help="Archivo NDJSON ECS")
    ap.add_argument("--config", default="config/parser/config.yaml")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    detectors = [Detector(d["name"], d["pattern"], d["type"]) for d in cfg.get("detectors", [])]

    input_dir = Path(args.inp)
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as out_f:
        for log_file in sorted((input_dir).glob("*")):
            if not log_file.is_file():
                continue
            log_type = guess_type(log_file, detectors) or "unknown"
            with log_file.open("r", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    doc = parse_line(log_type, line)
                    if doc:
                        out_f.write(json.dumps(doc) + "\n")

    print(f"[OK] NDJSON ECS => {output_path}")

if __name__ == "__main__":
    main()
