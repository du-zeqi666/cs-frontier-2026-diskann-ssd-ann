import re
import csv
from pathlib import Path

LOG_DIR = Path.home() / "ann_exp" / "log"
OUT = Path.home() / "ann_exp" / "result" / "task2_baseline_eval1000.csv"

def parse_timev(text):
    rss = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    fin = re.search(r"File system inputs:\s*(\d+)", text)
    fout = re.search(r"File system outputs:\s*(\d+)", text)
    elapsed = re.search(r"Elapsed \(wall clock\) time.*:\s*([0-9:.]+)", text)
    return {
        "max_rss_mb": round(int(rss.group(1)) / 1024, 2) if rss else "",
        "fs_inputs": int(fin.group(1)) if fin else "",
        "fs_outputs": int(fout.group(1)) if fout else "",
        "elapsed": elapsed.group(1) if elapsed else "",
    }

def parse_memory(text):
    # L QPS AvgDistCmps MeanLatency P999 Recall
    rows = []
    for line in text.splitlines():
        p = line.split()
        if len(p) == 6:
            try:
                rows.append({
                    "L": int(p[0]),
                    "qps": float(p[1]),
                    "avg_dist_cmps": float(p[2]),
                    "mean_latency_us": float(p[3]),
                    "p999_latency_us": float(p[4]),
                    "recall@10": float(p[5]),
                })
            except ValueError:
                pass
    return rows[-1] if rows else None

def parse_disk(text):
    # L Beamwidth QPS MeanLatency P999 MeanIOs MeanIOus CPU Recall
    rows = []
    for line in text.splitlines():
        p = line.split()
        if len(p) == 9:
            try:
                rows.append({
                    "L": int(p[0]),
                    "beamwidth": int(p[1]),
                    "qps": float(p[2]),
                    "mean_latency_us": float(p[3]),
                    "p999_latency_us": float(p[4]),
                    "mean_ios": float(p[5]),
                    "mean_io_us": float(p[6]),
                    "cpu_s": float(p[7]),
                    "recall@10": float(p[8]),
                })
            except ValueError:
                pass
    return rows[-1] if rows else None

def main():
    rows = []

    for path in sorted(LOG_DIR.glob("search_memory_sift1m_eval1000_L*.log")):
        text = path.read_text(errors="ignore")
        m = parse_memory(text)
        if not m:
            continue
        t = parse_timev(text)
        rows.append({
            "dataset": "sift1m_eval1000",
            "method": "memory",
            "L": m["L"],
            "beamwidth": 0,
            "cache_nodes": 0,
            "threads": 4,
            "recall@10": m["recall@10"],
            "qps": m["qps"],
            "mean_latency_us": m["mean_latency_us"],
            "p999_latency_us": m["p999_latency_us"],
            "avg_dist_cmps": m["avg_dist_cmps"],
            "mean_ios": "",
            "mean_io_us": "",
            "io_time_ratio": "",
            "max_rss_mb": t["max_rss_mb"],
            "fs_inputs": t["fs_inputs"],
            "fs_outputs": t["fs_outputs"],
            "elapsed": t["elapsed"],
            "log": path.name,
        })

    for path in sorted(LOG_DIR.glob("search_disk_sift1m_eval1000_L*_W2_cache0.log")):
        text = path.read_text(errors="ignore")
        d = parse_disk(text)
        if not d:
            continue
        t = parse_timev(text)
        ratio = d["mean_io_us"] / d["mean_latency_us"] if d["mean_latency_us"] else ""
        rows.append({
            "dataset": "sift1m_eval1000",
            "method": "disk",
            "L": d["L"],
            "beamwidth": d["beamwidth"],
            "cache_nodes": 0,
            "threads": 4,
            "recall@10": d["recall@10"],
            "qps": d["qps"],
            "mean_latency_us": d["mean_latency_us"],
            "p999_latency_us": d["p999_latency_us"],
            "avg_dist_cmps": "",
            "mean_ios": d["mean_ios"],
            "mean_io_us": d["mean_io_us"],
            "io_time_ratio": ratio,
            "max_rss_mb": t["max_rss_mb"],
            "fs_inputs": t["fs_inputs"],
            "fs_outputs": t["fs_outputs"],
            "elapsed": t["elapsed"],
            "log": path.name,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "dataset","method","L","beamwidth","cache_nodes","threads",
        "recall@10","qps","mean_latency_us","p999_latency_us",
        "avg_dist_cmps","mean_ios","mean_io_us","io_time_ratio",
        "max_rss_mb","fs_inputs","fs_outputs","elapsed","log"
    ]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {OUT}, rows={len(rows)}")
    for r in rows:
        print(r)

if __name__ == "__main__":
    main()
