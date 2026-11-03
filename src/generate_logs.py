"""Generate a synthetic distributed-system log file with injected anomalies."""
import random
from datetime import datetime, timedelta
from pathlib import Path

NODES = [f"node-{i}" for i in range(1, 6)]

NORMAL_TEMPLATES = [
    "Block blk_{blk} received from {ip}",
    "Block blk_{blk} replicated to {ip} in {ms} ms",
    "Heartbeat received from {node}",
    "Request {req} completed in {ms} ms",
    "User session {req} authenticated successfully",
    "Cache hit for key {req}",
    "Checkpoint saved at offset {req}",
]

ANOMALY_TEMPLATES = [
    "ERROR Failed to replicate block blk_{blk} to {ip}: connection refused",
    "ERROR Timeout waiting for heartbeat from {node}",
    "WARN Disk usage critical on {node}: {ms} percent",
    "ERROR Unexpected exception in request {req}: NullPointerException",
    "ERROR Node {node} unreachable, retrying",
]


def _fill(template: str) -> str:
    return template.format(
        blk=random.randint(10**8, 10**9),
        ip=f"10.0.{random.randint(0, 9)}.{random.randint(1, 254)}",
        ms=random.randint(1, 900),
        req=random.randint(1000, 99999),
        node=random.choice(NODES),
    )


def generate(n_lines=20000, anomaly_rate=0.01, seed=42, out_dir="data"):
    random.seed(seed)
    out = Path(out_dir)
    out.mkdir(exist_ok=True)
    t = datetime(2026, 1, 1, 0, 0, 0)
    lines, labels = [], []
    burst_left = 0
    for _ in range(n_lines):
        t += timedelta(seconds=random.randint(0, 2))
        if burst_left == 0 and random.random() < anomaly_rate / 4:
            burst_left = random.randint(3, 6)  # anomalies come in bursts
        if burst_left > 0:
            msg, level, label = _fill(random.choice(ANOMALY_TEMPLATES)), "", 1
            burst_left -= 1
        else:
            msg, level, label = _fill(random.choice(NORMAL_TEMPLATES)), "INFO", 0
        node = random.choice(NODES)
        lines.append(f"{t:%Y-%m-%d %H:%M:%S} {level} [{node}] {msg}".replace("  ", " "))
        labels.append(label)
    (out / "system.log").write_text("\n".join(lines), encoding="utf-8")
    (out / "labels.txt").write_text("\n".join(map(str, labels)), encoding="utf-8")
    print(f"Generated {n_lines} log lines, {sum(labels)} anomalous -> {out}/system.log")


if __name__ == "__main__":
    generate()
