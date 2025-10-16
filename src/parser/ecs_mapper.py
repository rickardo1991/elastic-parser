import re
from datetime import datetime, timezone

APACHE_RE = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+[^"]+"\s+(?P<status>\d{3})\s+(?P<size>\d+)(?:\s+"(?P<ref>[^"]*)")?(?:\s+"(?P<ua>[^"]*)")?'
)

SYSLOG_RE = re.compile(
    r'^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+(?P<proc>[\w\-/]+)(?:\[\d+\])?:\s+(?P<msg>.*)$'
)

MONTHS = {m: i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], start=1)}

def apache_to_ecs(line: str) -> dict:
    m = APACHE_RE.search(line)
    if not m:
        return {}
    ts = datetime.strptime(m.group("ts"), "%d/%b/%Y:%H:%M:%S %z").astimezone(timezone.utc).isoformat()
    return {
        "@timestamp": ts,
        "ecs": {"version": "8.11.0"},
        "event": {"category": ["web"], "kind": "event"},
        "source": {"ip": m.group("ip")},
        "http": {
            "request": {"method": m.group("method")},
            "response": {"status_code": int(m.group("status"))}
        },
        "url": {"original": m.group("url")},
        "user_agent": {"original": m.group("ua") or ""},
    }

def syslog_to_ecs(line: str) -> dict:
    m = SYSLOG_RE.search(line)
    if not m:
        return {}
    # Year-less syslog: asumimos año actual y UTC
    now = datetime.now(timezone.utc)
    mon = MONTHS[m.group("mon")]
    day = int(m.group("day"))
    hh, mm, ss = map(int, m.group("time").split(":"))
    ts = datetime(now.year, mon, day, hh, mm, ss, tzinfo=timezone.utc).isoformat()
    return {
        "@timestamp": ts,
        "ecs": {"version": "8.11.0"},
        "event": {"category": ["process"], "kind": "event"},
        "host": {"hostname": m.group("host")},
        "process": {"name": m.group("proc")},
        "log": {"level": "", "syslog": {"original": line}},
        "message": m.group("msg"),
    }
