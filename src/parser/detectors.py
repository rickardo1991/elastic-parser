import re
from pathlib import Path
from typing import Optional

class Detector:
    def __init__(self, name: str, pattern: str, type_name: str):
        self.name = name
        self.pattern = re.compile(pattern)

        # type is reserved in Python builtins
        self.type_name = type_name

    def match(self, line: str) -> bool:
        return bool(self.pattern.search(line))

def guess_type(sample_path: Path, detectors: list[Detector]) -> Optional[str]:
    with sample_path.open("r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            for d in detectors:
                if d.match(line):
                    return d.type_name
    return None
