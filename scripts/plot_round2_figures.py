#!/usr/bin/env python3
"""Round 2 figures for ADVANCED_REPORT.md."""
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


def fig_reorder_orig_vs_real(df, out):
    sub = df[(df["cache_nodes"] == 0) & (df["prefetch_lite"] == "off") &
             (df["reorder_mode"].isin(["none", "real"])) & (df["cache_mode"] == "node")].copy()
    sub["group"] = sub["method"].map({
        "static_bfs_orig": "Original (no perm)",
        "static_bfs_reord": "Real 4KB reorder",
    })
    fig, ax = plt.subplots(figsize=(8, 5))
    for grp, g in sub.groupby("group"):
        gg = g.sort_values(["L", "beamwidth"]).reset_index(drop=True)
        ax.plot(range(len(gg)), gg["qps"], "o-", label=grp, linewidth=2, markersize=10)
        for i, row in gg.iterrows():
            ax.annotate(f"L={int(row['L'])} W={int(row['beamwidth'])}",
                       (i, row["qps"]), textcoords="offset points", xytext=(0, 8),
                       fontsize=7, ha="center")
    ax.set_xticks(range(len(sub)))
    ax.set_xticklabels([f"L={int(r['L'])}\nW={int(r['beamwidth'])}" for _, r in sub.iterrows()],
                       rotation=0, fontsize=8)
    ax.set_ylabel("QPS (1 thread, cache=0)")
    ax.set_title("Real 4KB Reorder vs Original (random10k, cache=0, 1 thread)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, os.path.join(out, "reorder_orig_vs_real.png"))


def fig_block_cache_impact(df, out):
    sub = df[(df["cache_nodes"] == 1000) & (df["prefetch_lite"] == "off") &
             (df["reorder_mode"] == "real") &
             (df["cache_mode"].isin(["node", "block"]))].copy()
    sub["group"] = sub["cache_mode"].map({"node": "Node cache (BAC off)",
                                          "block": "Block-aware cache (BAC on)"})
    fig, ax = plt.subplots(figsize=(8, 5))
    for grp, g in sub.groupby("group"):
        gg = g.sort_values(["L", "beamwidth"]).reset_index(drop=True)
        ax.plot(range(len(gg)), gg["qps"], "s-", label=grp, linewidth=2, markersize=10)
    ax.set_xticks(range(len(sub)))
    ax.set_xticklabels([f"L={int(r['L'])}\nW={int(r['beamwidth'])}" for _, r in sub.iterrows()],
                       rotation=0, fontsize=8)
    ax.set_ylabel("QPS (1 thread, cache=1000)")
    ax.set_title("Block-aware Cache (BAC) Impact on QPS (random10k_reordered)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    save(fig, os.path.join(out, "block_cache_impact.png"))


def fig_prefetch_breakdown(df, out):
    sub = df[(df["cache_nodes"] == 1000) & (df["reorder_mode"] == "real") &
             (df["cache_mode"] == "block") & (df["L"] == 80)].copy()
    fig, ax = plt.subplots(figsize=(7, 4))
    for grp, g in sub.groupby("prefetch_lite"):
        ax.bar(grp, g["qps"].mean(), color=["#888" if grp == "off" else "#2ca02c"])
    ax.set_ylabel("Mean QPS (L=80, W=4, 1 thread)")
    ax.set_title("Prefetch-lite Impact (CPU hint before IO submission)")
    ax.grid(True, alpha=0.3, axis="y")
    save(fig, os.path.join(out, "prefetch_breakdown.png"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--out_dir", required=True)
    args = p.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    df = pd.read_csv(args.csv)
    fig_reorder_orig_vs_real(df, args.out_dir)
    fig_block_cache_impact(df, args.out_dir)
    fig_prefetch_breakdown(df, args.out_dir)
    print(f"\nAll figures saved to {args.out_dir}/")
    for f in sorted(os.listdir(args.out_dir)):
        if f.endswith(".png"):
            print(f"  {f}")


if __name__ == "__main__":
    main()
