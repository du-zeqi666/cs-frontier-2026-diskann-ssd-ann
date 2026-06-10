#!/usr/bin/env python3
"""
Generate 8 figures for the advanced experiment report.

Each plot uses only pandas + matplotlib (no seaborn, no numpy).
Paths injected via argparse (no hard-coding).
"""
import argparse
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Color and marker scheme
METHOD_COLORS = {
    "static_bfs": "#1f77b4",   # blue
    "hot":        "#ff7f0e",   # orange
    "hybrid":     "#2ca02c",   # green
}
METHOD_MARKERS = {
    "static_bfs": "o",
    "hot":        "^",
    "hybrid":     "s",
}


def save(fig, out_path):
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {out_path}")


def fig_cache_recall_qps(df, out_dir):
    """Fig 1: QPS vs Recall@10 at L=80, grouped by method, K marker shape = cache_nodes."""
    sub = df[df["L"] == 80]
    fig, ax = plt.subplots(figsize=(8, 5))
    for method, g in sub.groupby("method"):
        for k, gg in g.groupby("cache_nodes"):
            ax.scatter(gg["recall_at_10"], gg["qps"],
                       c=METHOD_COLORS.get(method, "#999"),
                       marker=METHOD_MARKERS.get(method, "x"),
                       s=80, alpha=0.7,
                       label=f"{method} K={k}" if k == sorted(sub[sub.method==method]["cache_nodes"].unique())[0] else None)
    ax.set_xlabel("Recall@10")
    ax.set_ylabel("QPS")
    ax.set_title("Cache Policy Comparison: Recall@10 vs QPS on SIFT1M (L=80, W=4, 4 threads, eval800)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=8)
    save(fig, os.path.join(out_dir, "cache_recall_qps.png"))


def fig_cache_size_io(df, out_dir):
    """Fig 2: mean_ios vs cache_nodes for static_bfs / hot at L=80."""
    sub = df[(df["L"] == 80) & (df["method"].isin(["static_bfs", "hot"]))]
    fig, ax = plt.subplots(figsize=(8, 5))
    for method, g in sub.groupby("method"):
        agg = g.groupby("cache_nodes")["mean_ios"].mean().sort_index()
        ax.plot(agg.index, agg.values, marker=METHOD_MARKERS.get(method, "x"),
                c=METHOD_COLORS.get(method, "#999"), label=method, linewidth=2, markersize=10)
    ax.set_xlabel("cache_nodes")
    ax.set_ylabel("mean_ios (per query)")
    ax.set_title("Cache Size vs Mean IOs (L=80, eval800)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, os.path.join(out_dir, "cache_size_io.png"))


def fig_hybrid_alpha_sweep(df, out_dir):
    """Fig 5: hybrid alpha sweep, QPS vs alpha at L=80,120,40."""
    sub = df[(df["method"] == "hybrid") & (df["cache_nodes"] == 10000)].copy()
    sub["alpha"] = sub["cache_policy"].str.replace("hybrid_a", "").astype(int) / 10.0
    fig, ax = plt.subplots(figsize=(8, 5))
    for L, g in sub.groupby("L"):
        gg = g.sort_values("alpha")
        ax.plot(gg["alpha"], gg["qps"], marker="o", linewidth=2, markersize=10, label=f"L={L}")
    ax.set_xlabel("alpha (BFS fraction in hybrid cache)")
    ax.set_ylabel("QPS")
    ax.set_title("Hybrid Cache: alpha Sweep (K=10000, eval800)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, os.path.join(out_dir, "hybrid_alpha_sweep.png"))


def fig_hot_cache_dist(out_dir, trace_path):
    """Fig 3: hot cache frequency distribution (top-10K vs tail)."""
    from collections import Counter
    counter = Counter()
    with open(trace_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            qid, ev, nid_s = parts
            if ev not in ("miss", "read"):
                continue
            try:
                counter[int(nid_s)] += 1
            except ValueError:
                continue
    most_common = counter.most_common()
    top10k = [c for _, c in most_common[:10000]]
    tail = [c for _, c in most_common[10000:]]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # Top-10K distribution
    axes[0].plot(range(len(top10k)), top10k, linewidth=0.6)
    axes[0].set_xlabel("rank (top-10K)")
    axes[0].set_ylabel("visit count")
    axes[0].set_title("Hot Cache: Top-10K Frequency Distribution")
    axes[0].grid(True, alpha=0.3)
    # Tail histogram
    if tail:
        axes[1].hist(tail, bins=50, color="orange", edgecolor="black")
        axes[1].set_xlabel("visit count (tail: rank > 10K)")
        axes[1].set_ylabel("# nodes")
        axes[1].set_yscale("log")
        axes[1].set_title(f"Hot Cache: Tail Distribution (n={len(tail)})")
        axes[1].grid(True, alpha=0.3)
    save(fig, os.path.join(out_dir, "hot_cache_dist.png"))


def fig_block_sim(csv_path, out_dir):
    """Fig 4: block sim compression ratio vs B."""
    df = pd.read_csv(csv_path)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["B"], df["compression_ratio"], marker="o", linewidth=2, markersize=10, color="#d62728")
    ax.set_xlabel("B (nodes per 4KB block)")
    ax.set_ylabel("compression_ratio (orig / reordered)")
    ax.set_title("4KB Block Locality: Compression Ratio vs B (co-access greedy reorder)")
    ax.grid(True, alpha=0.3)
    # annotate values
    for x, y in zip(df["B"], df["compression_ratio"]):
        ax.annotate(f"{y:.2f}x", (x, y), textcoords="offset points", xytext=(5, 5))
    save(fig, os.path.join(out_dir, "block_sim_compression.png"))


def fig_io_breakdown(df, out_dir):
    """Fig 7: stacked bar of IO time vs non-IO time per (method, L) at K=10000."""
    sub = df[(df["cache_nodes"] == 10000) | (df["method"] == "static_bfs")]
    sub = sub[sub["L"].isin([40, 80, 120])]
    sub = sub.copy()
    sub["label"] = sub["method"] + "_L" + sub["L"].astype(str)
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = sub["label"].tolist()
    io_us = sub["mean_io_us"].tolist()
    non_io = sub["non_io_us"].tolist()
    import itertools
    x = list(range(len(labels)))
    ax.bar(x, io_us, color="#1f77b4", label="io_us")
    ax.bar(x, non_io, bottom=io_us, color="#ff7f0e", label="non_io_us")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("microseconds per query")
    ax.set_title("IO Time vs Non-IO Time Composition (cache_nodes=10000)")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    save(fig, os.path.join(out_dir, "io_cpu_breakdown.png"))


def fig_latency_tail(df, out_dir):
    """Fig 8: p999 latency per method (since p95/p99 not available)."""
    sub = df[df["L"] == 80]
    fig, ax = plt.subplots(figsize=(8, 5))
    for method, g in sub.groupby("method"):
        agg = g.groupby("cache_nodes")["p999_latency_us"].mean().sort_index()
        ax.plot(agg.index, agg.values, marker=METHOD_MARKERS.get(method, "x"),
                c=METHOD_COLORS.get(method, "#999"), label=method, linewidth=2, markersize=10)
    ax.set_xlabel("cache_nodes")
    ax.set_ylabel("p99.9 latency (us)")
    ax.set_title("Latency Tail (p99.9) vs Cache Size (L=80, eval800)")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, os.path.join(out_dir, "latency_tail.png"))


def fig_method_io_compare(df, out_dir):
    """Fig: mean_ios grouped by method for fixed L=80, K=10000."""
    sub = df[(df["L"] == 80) & (df["cache_nodes"] == 10000)]
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (method, g) in enumerate(sub.groupby("method")):
        if g.empty: continue
        # For hybrid, group by alpha
        if method == "hybrid":
            gg = g.copy()
            gg["alpha"] = gg["cache_policy"].str.replace("hybrid_a", "").astype(int) / 10.0
            gg = gg.sort_values("alpha")
            ax.plot(gg["alpha"], gg["mean_ios"], marker="s", linewidth=2, markersize=8,
                    color=METHOD_COLORS.get(method, "#999"), label=f"{method} (alpha sweep)")
        else:
            ax.scatter([0.0], [g["mean_ios"].mean()],
                       c=METHOD_COLORS.get(method, "#999"),
                       marker=METHOD_MARKERS.get(method, "x"),
                       s=200, label=method)
    ax.set_xlabel("alpha (only for hybrid)")
    ax.set_ylabel("mean_ios (L=80)")
    ax.set_title("Mean IOs per Method (K=10000, L=80)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, os.path.join(out_dir, "method_io_compare.png"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="advanced_all.csv")
    parser.add_argument("--block_csv", required=True, help="block_sim.csv")
    parser.add_argument("--trace", required=True, help="trace_200q.txt for hot cache dist")
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    df = pd.read_csv(args.csv)
    print(f"Loaded {len(df)} rows from {args.csv}")

    fig_cache_recall_qps(df, args.out_dir)
    fig_cache_size_io(df, args.out_dir)
    fig_hybrid_alpha_sweep(df, args.out_dir)
    fig_hot_cache_dist(args.out_dir, args.trace)
    fig_block_sim(args.block_csv, args.out_dir)
    fig_io_breakdown(df, args.out_dir)
    fig_latency_tail(df, args.out_dir)
    fig_method_io_compare(df, args.out_dir)

    print(f"\nAll figures saved to {args.out_dir}/")
    for f in sorted(os.listdir(args.out_dir)):
        if f.endswith(".png"):
            print(f"  {f}")


if __name__ == "__main__":
    main()
