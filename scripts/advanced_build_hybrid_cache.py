#!/usr/bin/env python3
"""
Build a hybrid cache list: alpha-fraction of BFS + (1-alpha)-fraction of hot.
Dedup, fill to total K.

Input format: cache list file (header line = count, then one uint per line).
Output format: same.
"""
import argparse


def read_ids(path):
    with open(path) as f:
        n = int(f.readline().strip())
        ids = [int(f.readline().strip()) for _ in range(n)]
    return ids


def write_ids(path, ids):
    with open(path, "w") as f:
        f.write(f"{len(ids)}\n")
        for nid in ids:
            f.write(f"{nid}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bfs_src", required=True)
    parser.add_argument("--hot_src", required=True)
    parser.add_argument("--alpha", type=float, required=True,
                        help="fraction taken from BFS (0..1); rest from hot")
    parser.add_argument("--total", type=int, required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    bfs_list = read_ids(args.bfs_src)
    hot_list = read_ids(args.hot_src)
    n_bfs = int(args.alpha * args.total)
    n_hot = args.total - n_bfs
    print(f"BFS source: {len(bfs_list)} ids, taking first {n_bfs}")
    print(f"Hot source: {len(hot_list)} ids, taking first {n_hot}")

    bfs_part = bfs_list[:n_bfs]
    hot_part = hot_list[:n_hot]
    seen = set()
    merged = []
    for nid in bfs_part + hot_part:
        if nid not in seen:
            seen.add(nid)
            merged.append(nid)
        if len(merged) == args.total:
            break
    # tail fill with remaining hot nodes
    if len(merged) < args.total:
        for nid in hot_list:
            if len(merged) == args.total:
                break
            if nid not in seen:
                seen.add(nid)
                merged.append(nid)

    eff_alpha = len(bfs_part) / max(len(merged), 1)
    print(f"Merged: {len(merged)} unique ids; effective alpha = {eff_alpha:.3f} (nominal {args.alpha})")
    write_ids(args.out, merged)
    print(f"  -> {args.out}")


if __name__ == "__main__":
    main()
