#!/usr/bin/env python3
"""
Aggregate advanced experiment logs into a 27-field CSV.

Fields (per spec):
dataset, method, advanced_task, cache_policy, cache_nodes,
L, beamwidth, threads,
recall@10, qps, mean_latency_us,
p95_latency_us, p99_latency_us, p999_latency_us,
mean_ios, mean_io_us, io_time_ratio_pct,
non_io_us, non_io_time_ratio_pct,
max_rss_mb, index_size_mb, cache_size_mb,
trace_queries, eval_queries, log, git_commit, notes
"""
import argparse
import csv
import os
import re


INDEX_SIZE_MB = 822.37  # from task3 index_size_summary (sift1m disk total)
GIT_COMMIT = "78256bba"  # recorded in git_state_phase1.txt

# match per-L data line: e.g. "    80           4          567.32         6986.69         9925.00           84.84         6476.08          340.13           97.62"
DATA_LINE_RE = re.compile(
    r"^\s*(?P<L>\d+)\s+(?P<W>\d+)\s+(?P<QPS>[\d\.]+)\s+(?P<lat>[\d\.]+)\s+(?P<lat999>[\d\.]+)\s+(?P<ios>[\d\.]+)\s+(?P<io_us>[\d\.]+)\s+(?P<cpu_s>[\d\.]+)\s+(?P<recall>[\d\.]+)\s*$"
)


def parse_log(log_path):
    """Return list of dicts: one per L value."""
    out = []
    with open(log_path) as f:
        for line in f:
            m = DATA_LINE_RE.match(line)
            if m:
                d = m.groupdict()
                out.append({
                    "L": int(d["L"]),
                    "W": int(d["W"]),
                    "qps": float(d["QPS"]),
                    "mean_latency_us": float(d["lat"]),
                    "p999_latency_us": float(d["lat999"]),
                    "mean_ios": float(d["ios"]),
                    "mean_io_us": float(d["io_us"]),
                    "cpu_s": float(d["cpu_s"]),
                    "recall_at_10": float(d["recall"]),
                })
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", required=True, help="e.g. /home/dzq/ann_exp/log/advanced_cache")
    parser.add_argument("--out", required=True)
    parser.add_argument("--trace_queries", type=int, default=200)
    parser.add_argument("--eval_queries", type=int, default=800)
    args = parser.parse_args()

    # Map log filename to (method, cache_policy, cache_nodes)
    # Convention used in this experiment:
    #   static_bfs_K{L}.log        -> method=disk, policy=bfs,  cache_nodes=L
    #   hot_K{L}_L{L}.log          -> method=disk, policy=hot,  cache_nodes=L
    #   hybrid_a{ATAG}_L{L}.log    -> method=disk, policy=hybrid_a{ATAG}, cache_nodes=10000
    rows = []
    for fname in sorted(os.listdir(args.log_dir)):
        if not fname.endswith(".log"):
            continue
        full = os.path.join(args.log_dir, fname)
        for entry in parse_log(full):
            if fname.startswith("static_bfs_K"):
                m = re.match(r"static_bfs_K(\d+)_L(\d+)\.log", fname)
                if not m: continue
                cache_nodes = int(m.group(1))
                L = int(m.group(2))
                method = "static_bfs"
                policy = "bfs"
            elif fname.startswith("hot_K"):
                m = re.match(r"hot_K(\d+)_L(\d+)\.log", fname)
                if not m: continue
                cache_nodes = int(m.group(1))
                L = int(m.group(2))
                method = "hot"
                policy = "hot_freq"
            elif fname.startswith("hybrid_a"):
                m = re.match(r"hybrid_a(\d+)_L(\d+)\.log", fname)
                if not m: continue
                alpha_tag = m.group(1)
                L = int(m.group(2))
                cache_nodes = 10000
                method = "hybrid"
                policy = f"hybrid_a{alpha_tag}"
            else:
                continue

            # IO time ratio
            mean_io_us = entry["mean_io_us"]
            mean_lat = entry["mean_latency_us"]
            io_time_ratio = (mean_io_us / mean_lat * 100) if mean_lat > 0 else 0
            non_io_us = mean_lat - mean_io_us
            non_io_ratio = 100 - io_time_ratio

            # RSS MB: not available from per-query stats; leave 0
            max_rss_mb = 0
            # cache size MB: cache_nodes * (max_degree+1) * 4 + cache_nodes * aligned_dim * 4
            # For SIFT1M, R=64, dim=128. Rough estimate:
            #   per cached node: 64*4 (nbr) + 128*4 (coord) = 768 bytes
            #   cache_nodes=10000 -> ~7.3 MB; K=1000 -> 0.73 MB
            cache_size_mb = cache_nodes * (64 + 128) * 4 / (1024 * 1024)

            rows.append({
                "dataset": "sift1m",
                "method": method,
                "advanced_task": "T2_cache" if method != "static_bfs" else "T3_baseline",
                "cache_policy": policy,
                "cache_nodes": cache_nodes,
                "L": L,
                "beamwidth": entry["W"],
                "threads": 4,
                "recall_at_10": entry["recall_at_10"] / 100,  # convert to fraction
                "qps": entry["qps"],
                "mean_latency_us": mean_lat,
                "p95_latency_us": "",  # not available
                "p99_latency_us": "",
                "p999_latency_us": entry["p999_latency_us"],
                "mean_ios": entry["mean_ios"],
                "mean_io_us": mean_io_us,
                "io_time_ratio_pct": round(io_time_ratio, 2),
                "non_io_us": round(non_io_us, 2),
                "non_io_time_ratio_pct": round(non_io_ratio, 2),
                "max_rss_mb": max_rss_mb,
                "index_size_mb": INDEX_SIZE_MB,
                "cache_size_mb": round(cache_size_mb, 2),
                "trace_queries": args.trace_queries,
                "eval_queries": args.eval_queries,
                "log": fname,
                "git_commit": GIT_COMMIT,
                "notes": "",
            })

    fieldnames = list(rows[0].keys()) if rows else []
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
