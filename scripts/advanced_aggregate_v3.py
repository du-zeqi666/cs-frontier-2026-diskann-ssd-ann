#!/usr/bin/env python3
"""v5.1 aggregator: 34 runs from advanced_real_reorder_v5/ → CSV with new fields.

Adds 2 fields vs v2: n_node_io_requests, n_unique_sectors (from v5 P0-3/P0-4
sector-dedup instrumentation).
"""
import csv
import os
import re

LOG_DIR = "/home/dzq/ann_exp/log/advanced_real_reorder_v5"
OUT = "/home/dzq/ann_exp/result/advanced_real_reorder_v5.csv"

# v5.1 per-query line: L W QPS mean_lat p999 mean_ios mean_io_us cpu_s
#   node_reqs unique_sec dedup% [recall]
# Print order from apps/search_disk_index.cpp:
#   L, W, QPS, lat, p999, mean_ios, mean_io_us, cpu_s, node_reqs,
#   unique_sec, dedup% [, recall]
LINE_RE = re.compile(
    r"^\s*(?P<L>\d+)\s+(?P<W>\d+)\s+(?P<qps>[\d\.]+)\s+(?P<lat>[\d\.]+)\s+"
    r"(?P<lat999>[\d\.]+)\s+(?P<ios>[\d\.]+)\s+(?P<io_us>[\d\.]+)\s+"
    r"(?P<cpu_s>[\d\.]+)\s+(?P<node_reqs>[\d\.]+)\s+"
    r"(?P<unique_sec>[\d\.]+)\s+(?P<dedup>[\d\.]+)"
    r"(?:\s+(?P<recall>[\d\.]+))?\s*$"
)


def classify(fname):
    # v5.1 G.1: r10k_bac${BAC}_K${K}_L${L}.log
    if fname.startswith("r10k_bac"):
        m = re.match(r"r10k_bac(?P<bac>off|on)_K(?P<K>\d+)_L(?P<L>\d+)\.log", fname)
        if m:
            return {
                "method": "bfs_cache_reord",
                "reorder_mode": "real",
                "cache_mode": "block" if m["bac"] == "on" else "node",
                "prefetch_lite": "off",
                "cache_nodes": int(m["K"]),
                "L": int(m["L"]),
                "beamwidth": 4,
            }
    # v5.1 G.2: r10k_${TAG}_L${L}_W${W}.log
    m = re.match(r"r10k_(?P<tag>orig|reord)_L(?P<L>\d+)_W(?P<W>\d+)\.log", fname)
    if m:
        return {
            "method": "static_bfs_reord" if m["tag"] == "reord" else "static_bfs_orig",
            "reorder_mode": "real" if m["tag"] == "reord" else "none",
            "cache_mode": "node",
            "prefetch_lite": "off",
            "cache_nodes": 0,
            "L": int(m["L"]),
            "beamwidth": int(m["W"]),
        }
    return None


fields = [
    "dataset", "method", "advanced_task", "cache_policy", "cache_nodes",
    "L", "beamwidth", "threads",
    "recall_at_10", "qps", "mean_latency_us",
    "p95_latency_us", "p99_latency_us", "p999_latency_us",
    "mean_ios", "mean_io_us", "io_time_ratio_pct",
    "non_io_us", "non_io_time_ratio_pct",
    "max_rss_mb", "index_size_mb", "cache_size_mb",
    "trace_queries", "eval_queries", "log", "git_commit", "notes",
    "reorder_mode", "cache_mode", "prefetch_lite",
    "n_node_io_requests", "n_unique_sectors",
]

rows = []
for fname in sorted(os.listdir(LOG_DIR)):
    if not fname.endswith(".log"):
        continue
    klass = classify(fname)
    if klass is None:
        continue
    full = os.path.join(LOG_DIR, fname)
    with open(full) as f:
        for line in f:
            m = LINE_RE.match(line)
            if m:
                d = m.groupdict()
                lat = float(d["lat"])
                io_us = float(d["io_us"])
                io_ratio = io_us / lat * 100 if lat > 0 else 0
                rows.append({
                    "dataset": "random10k",
                    "method": klass["method"],
                    "advanced_task": "T_real_reorder_v5",
                    "cache_policy": "bfs" if "bfs" in klass["method"] else "none",
                    "cache_nodes": klass["cache_nodes"],
                    "L": klass["L"],
                    "beamwidth": klass["beamwidth"],
                    "threads": 1,
                    "recall_at_10": 0.0,  # placeholder, set later if d["recall"] exists
                    "qps": float(d["qps"]),
                    "mean_latency_us": lat,
                    "p95_latency_us": "",
                    "p99_latency_us": "",
                    "p999_latency_us": float(d["lat999"]),
                    "mean_ios": float(d["ios"]),
                    "mean_io_us": io_us,
                    "io_time_ratio_pct": round(io_ratio, 2),
                    "non_io_us": round(lat - io_us, 2),
                    "non_io_time_ratio_pct": round(100 - io_ratio, 2),
                    "max_rss_mb": 0,
                    "index_size_mb": 6.8,
                    "cache_size_mb": round(klass["cache_nodes"] * 644 / 1024 / 1024, 4) if klass["cache_nodes"] else 0,
                    "trace_queries": 0,
                    "eval_queries": 1000,
                    "log": fname,
                    "git_commit": "78256bba",
                    "notes": "v5.1 real sector-dedup on random10k",
                    "reorder_mode": klass["reorder_mode"],
                    "cache_mode": klass["cache_mode"],
                    "prefetch_lite": klass["prefetch_lite"],
                    "n_node_io_requests": float(d["node_reqs"]),
                    "n_unique_sectors": float(d["unique_sec"]),
                })
                # recall is optional; if missing, set to 0 (degrades gracefully)
                if d["recall"] is None:
                    rows[-1]["recall_at_10"] = 0.0
                else:
                    rows[-1]["recall_at_10"] = float(d["recall"]) / 100

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to {OUT}")
