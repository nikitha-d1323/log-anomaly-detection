"""Log parsing and NLP preprocessing: raw lines -> clean templates -> TF-IDF vectors."""
import re
from pathlib import Path

import pandas as pd

LOG_PATTERN = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?:(?P<level>INFO|WARN|ERROR) )?\[(?P<node>[^\]]+)\] (?P<msg>.*)$"
)


def parse_logs(log_path="data/system.log", label_path="data/labels.txt"):
    rows = []
    for line in Path(log_path).read_text(encoding="utf-8").splitlines():
        m = LOG_PATTERN.match(line)
        if m:
            rows.append(m.groupdict())
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["ts"])
    df["level"] = df["level"].fillna("INFO")
    if Path(label_path).exists():
        labels = Path(label_path).read_text().split()
        df["label"] = [int(x) for x in labels[: len(df)]]
    return df.drop(columns=["ts"])


def clean_message(msg: str) -> str:
    """Turn a raw message into a template by masking variable parts."""
    msg = msg.lower()
    msg = re.sub(r"blk_\d+", "blk", msg)
    msg = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "ip", msg)
    msg = re.sub(r"\b\d+\b", "num", msg)
    msg = re.sub(r"[^a-z ]", " ", msg)
    return re.sub(r"\s+", " ", msg).strip()


def add_templates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["template"] = df["msg"].map(clean_message)
    return df


if __name__ == "__main__":
    d = add_templates(parse_logs())
    print(d[["level", "node", "template"]].head(10))
    print("\nUnique templates:", d["template"].nunique())
