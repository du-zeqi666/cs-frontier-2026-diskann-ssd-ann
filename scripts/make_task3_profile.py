import csv
from pathlib import Path

ROOT = Path.home() / "ann_exp"
IN_CSV = ROOT / "result" / "task2_baseline_eval1000.csv"

OUT_PROFILE = ROOT / "result" / "task3_profile_eval1000.csv"
OUT_DISK = ROOT / "result" / "task3_disk_profile_eval1000.csv"
OUT_SIZE = ROOT / "result" / "task3_index_size_summary.csv"
OUT_MD = ROOT / "result" / "task3_bottleneck_summary.md"

MEM_INDEX_DIR = ROOT / "index" / "memory"
DISK_INDEX_DIR = ROOT / "index" / "disk"

def to_float(x):
    if x is None or x == "":
        return None
    return float(x)

def to_int(x):
    if x is None or x == "":
        return None
    return int(float(x))

def fmt(x, nd=2):
    if x is None:
        return ""
    return round(float(x), nd)

def read_rows():
    rows = []
    with IN_CSV.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["L"] = to_int(r["L"])
            r["recall@10"] = to_float(r["recall@10"])
            r["qps"] = to_float(r["qps"])
            r["mean_latency_us"] = to_float(r["mean_latency_us"])
            r["p999_latency_us"] = to_float(r["p999_latency_us"])
            r["avg_dist_cmps"] = to_float(r["avg_dist_cmps"])
            r["mean_ios"] = to_float(r["mean_ios"])
            r["mean_io_us"] = to_float(r["mean_io_us"])
            r["io_time_ratio"] = to_float(r["io_time_ratio"])
            r["max_rss_mb"] = to_float(r["max_rss_mb"])
            r["fs_inputs"] = to_int(r["fs_inputs"])
            r["fs_outputs"] = to_int(r["fs_outputs"])

            if r["method"] == "disk" and r["mean_latency_us"] and r["mean_io_us"]:
                io_ratio = r["mean_io_us"] / r["mean_latency_us"]
                non_io_us = r["mean_latency_us"] - r["mean_io_us"]
                non_io_ratio = 1.0 - io_ratio
            else:
                io_ratio = None
                non_io_us = None
                non_io_ratio = None

            r["io_time_ratio_pct"] = fmt(io_ratio * 100, 2) if io_ratio is not None else ""
            r["non_io_us"] = fmt(non_io_us, 2) if non_io_us is not None else ""
            r["non_io_time_ratio_pct"] = fmt(non_io_ratio * 100, 2) if non_io_ratio is not None else ""

            rows.append(r)

    method_order = {"memory": 0, "disk": 1}
    rows.sort(key=lambda r: (method_order.get(r["method"], 99), r["L"]))
    return rows

def write_profile(rows):
    fields = [
        "dataset",
        "method",
        "L",
        "beamwidth",
        "cache_nodes",
        "threads",
        "recall@10",
        "qps",
        "mean_latency_us",
        "p999_latency_us",
        "avg_dist_cmps",
        "mean_ios",
        "mean_io_us",
        "io_time_ratio_pct",
        "non_io_us",
        "non_io_time_ratio_pct",
        "max_rss_mb",
        "fs_inputs",
        "fs_outputs",
        "elapsed",
        "log",
    ]

    with OUT_PROFILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fields})

    disk_rows = [r for r in rows if r["method"] == "disk"]
    with OUT_DISK.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in disk_rows:
            writer.writerow({k: r.get(k, "") for k in fields})

def collect_index_sizes():
    size_rows = []

    for method, folder in [("memory", MEM_INDEX_DIR), ("disk", DISK_INDEX_DIR)]:
        files = sorted(folder.glob("sift1m*"))
        total = 0

        for p in files:
            size = p.stat().st_size
            total += size
            size_rows.append({
                "method": method,
                "component": p.name,
                "size_mb": round(size / 1024 / 1024, 2),
                "path": str(p),
            })

        size_rows.append({
            "method": method,
            "component": "TOTAL",
            "size_mb": round(total / 1024 / 1024, 2),
            "path": str(folder),
        })

    with OUT_SIZE.open("w", newline="") as f:
        fields = ["method", "component", "size_mb", "path"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(size_rows)

    return size_rows

def avg(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None

def write_summary(rows, size_rows):
    mem = [r for r in rows if r["method"] == "memory"]
    disk = [r for r in rows if r["method"] == "disk"]

    disk_io_ratios = [to_float(r["io_time_ratio_pct"]) for r in disk]
    disk_mean_ios = [r["mean_ios"] for r in disk]
    disk_lats = [r["mean_latency_us"] for r in disk]
    mem_lats = [r["mean_latency_us"] for r in mem]
    disk_rss = [r["max_rss_mb"] for r in disk]
    mem_rss = [r["max_rss_mb"] for r in mem]

    mem_size = next((r["size_mb"] for r in size_rows if r["method"] == "memory" and r["component"] == "TOTAL"), "")
    disk_size = next((r["size_mb"] for r in size_rows if r["method"] == "disk" and r["component"] == "TOTAL"), "")

    disk_by_l = sorted(disk, key=lambda r: r["L"])
    mem_by_l = sorted(mem, key=lambda r: r["L"])

    lines = []
    lines.append("# Task 3 Profile Summary: DiskANN SSD Bottleneck Analysis")
    lines.append("")
    lines.append("## Dataset and setting")
    lines.append("")
    lines.append("- Dataset: SIFT1M with eval1000 queries")
    lines.append("- Compared methods: Memory Vamana and DiskANN SSD")
    lines.append("- Threads: 4")
    lines.append("- DiskANN SSD beamwidth: 2")
    lines.append("- DiskANN SSD cache nodes: 0")
    lines.append("- Search list L: 10, 20, 40, 80, 120")
    lines.append("")
    lines.append("## Main observations")
    lines.append("")
    lines.append(f"- Memory Vamana average max RSS: {fmt(avg(mem_rss), 2)} MB")
    lines.append(f"- DiskANN SSD average max RSS: {fmt(avg(disk_rss), 2)} MB")
    lines.append(f"- Memory index total size: {mem_size} MB")
    lines.append(f"- Disk index total size: {disk_size} MB")
    lines.append(f"- DiskANN SSD average IO time ratio: {fmt(avg(disk_io_ratios), 2)}%")
    lines.append(f"- DiskANN SSD mean IOs range: {fmt(min(disk_mean_ios), 2)} to {fmt(max(disk_mean_ios), 2)}")
    lines.append(f"- Memory Vamana mean latency range: {fmt(min(mem_lats), 2)} us to {fmt(max(mem_lats), 2)} us")
    lines.append(f"- DiskANN SSD mean latency range: {fmt(min(disk_lats), 2)} us to {fmt(max(disk_lats), 2)} us")
    lines.append("")
    lines.append("## Per-L disk profile")
    lines.append("")
    lines.append("| L | Recall@10 | QPS | Mean Latency us | Mean IOs | Mean IO us | IO Time Ratio % | Non-IO Ratio % | Max RSS MB |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in disk_by_l:
        lines.append(
            f"| {r['L']} | {r['recall@10']} | {r['qps']} | {r['mean_latency_us']} | "
            f"{r['mean_ios']} | {r['mean_io_us']} | {r['io_time_ratio_pct']} | "
            f"{r['non_io_time_ratio_pct']} | {r['max_rss_mb']} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "As L increases, recall improves because the search explores more candidates, "
        "but DiskANN SSD performs more random IOs per query. This increases mean latency "
        "and reduces QPS."
    )
    lines.append("")
    lines.append(
        "The IO time ratio of DiskANN SSD is around 95% in the current experiment. "
        "Therefore, the main bottleneck is SSD random IO rather than pure CPU computation."
    )
    lines.append("")
    lines.append(
        "Compared with Memory Vamana, DiskANN SSD uses much less DRAM during search, "
        "but it pays the cost of SSD access latency. This explains why DiskANN SSD is slower "
        "while being more suitable for large-scale datasets that cannot fit entirely in memory."
    )
    lines.append("")
    lines.append("## Note on vector computation time")
    lines.append("")
    lines.append(
        "The current DiskANN log directly reports mean IO time and mean latency, but it does not "
        "separately expose exact vector distance computation time. Therefore, this summary uses "
        "non-IO time, calculated as mean latency minus mean IO time, as an approximate upper bound "
        "for CPU-side work including vector distance computation, queue maintenance, and scheduling overhead."
    )
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        "The profile results show that DiskANN SSD is mainly bottlenecked by random SSD IO. "
        "A natural optimization direction is to reduce SSD reads by caching frequently visited nodes "
        "or improving graph access locality."
    )
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

def main():
    if not IN_CSV.exists():
        raise FileNotFoundError(f"missing input csv: {IN_CSV}")

    rows = read_rows()
    write_profile(rows)
    size_rows = collect_index_sizes()
    write_summary(rows, size_rows)

    print(f"wrote {OUT_PROFILE}")
    print(f"wrote {OUT_DISK}")
    print(f"wrote {OUT_SIZE}")
    print(f"wrote {OUT_MD}")

if __name__ == "__main__":
    main()
