#!/usr/bin/env python3
"""Task2 QPS-Recall curve for basic experiment (Memory Vamana vs DiskANN SSD).

Reads `task2_baseline_eval1000.csv` and plots:
  - x-axis: Recall@10
  - y-axis: QPS (log scale)
  - Memory Vamana and DiskANN SSD as two lines, with L labels.
"""
import argparse
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="/home/dzq/ann_exp/result/task2_baseline_eval1000.csv")
    ap.add_argument("--out", default="/home/dzq/ann_exp/figures/task2_qps_recall.png")
    args = ap.parse_args()
    df = pd.read_csv(args.csv)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = {"memory": "#4a90e2", "disk": "#e94e3b"}
    markers = {"memory": "o", "disk": "s"}
    for method, g in df.groupby("method"):
        gg = g.sort_values("recall@10").reset_index(drop=True)
        ax.plot(gg["recall@10"] * 100, gg["qps"],
                marker=markers.get(method, "o"),
                linewidth=2, markersize=10,
                color=colors.get(method, "gray"),
                label=("Memory Vamana" if method == "memory" else "DiskANN SSD"))
        for _, row in gg.iterrows():
            ax.annotate(f"L={int(row['L'])}",
                        (row["recall@10"] * 100, row["qps"]),
                        textcoords="offset points", xytext=(8, 5),
                        fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("Recall@10 (%)")
    ax.set_ylabel("QPS (log scale, 4 threads)")
    ax.set_title("Task2 Baseline: Memory Vamana vs DiskANN SSD (SIFT1M, 4 threads, 1000 queries)\n"
                 "DiskANN SSD is ~30-100x slower than Memory Vamana due to SSD IO ceiling")
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(loc="upper left", fontsize=10)
    save(fig, args.out)


if __name__ == "__main__":
    main()
