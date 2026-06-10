#!/usr/bin/env python3
"""Aggregate Round 2 (real implementation) logs into a single CSV."""
import csv
import os
import re

LOG_DIR = "/home/dzq/ann_exp/log/advanced_real_reorder"
OUT = "/home/dzq/ann_exp/result/advanced_real_reorder.csv"

# regex: "    L   W   QPS   mean_lat   p999   mean_ios   mean_io_us   cpu_s   recall"
LINE_RE = re.compile(
    r"^\s*(?P<L>\d+)\s+(?P<W>\d+)\s+(?P<qps>[\d\.]+)\s+(?P<lat>[\d\.]+)\s+"
    r"(?P<lat999>[\d\.]+)\s+(?P<ios>[\d\.]+)\s+(?P<io_us>[\d\.]+)\s+"
    r"(?P<cpu_s>[\d\.]+)\s+(?P<recall>[\d\.]+)\s*$"
)

# Map filename -> (method, cache_mode, prefetch_lite, reorder_mode)
def classify(fname):
    # orig_L40_W2.log  -> orig, node, off, none
    # reord_L40_W2.log -> reord, node, off, real
    # r10k_bacoff_...  -> reord, node, off, real
    # r10k_bacon_...   -> reord, block, off, real
    # r10k_prefetch_...-> reord, block, on, real
    if fname.startswith("orig_"):
        return ("static_bfs_orig", "node", "off", "none")
    if fname.startswith("reord_"):
        return ("static_bfs_reord", "node", "off", "real")
    if fname.startswith("r10k_bacoff_"):
        return ("bfs_cache_reord", "node", "off", "real")
    if fname.startswith("r10k_bacon_"):
        return ("bfs_cache_reord", "block", "off", "real")
    if fname.startswith("r10k_prefetch_"):
        return ("bfs_cache_reord", "block", "on", "real")
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
]

rows = []
for fname in sorted(os.listdir(LOG_DIR)):
    if not fname.endswith(".log"):
        continue
    klass = classify(fname)
    if klass is None:
        continue
    method, cache_mode, prefetch, reorder = klass
    cache_nodes = 0 if "cache" not in method or "orig" in method else 1000
    if "bfs_cache" in method:
        cache_nodes = 1000
    if method == "static_bfs_orig":
        cache_nodes = 0
    if method == "static_bfs_reord":
        cache_nodes = 0
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
                    "method": method,
                    "advanced_task": "T_real_reorder",
                    "cache_policy": "bfs" if "bfs" in method else "none",
                    "cache_nodes": cache_nodes,
                    "L": int(d["L"]),
                    "beamwidth": int(d["W"]),
                    "threads": 1,
                    "recall_at_10": float(d["recall"]) / 100,
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
                    "cache_size_mb": round(cache_nodes * 644 / 1024 / 1024, 4) if cache_nodes else 0,
                    "trace_queries": 0,
                    "eval_queries": 1000,
                    "log": fname,
                    "git_commit": "78256bba",
                    "notes": "Round 2 real implementation on random10k",
                    "reorder_mode": reorder,
                    "cache_mode": cache_mode,
                    "prefetch_lite": prefetch,
                })

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to {OUT}")
