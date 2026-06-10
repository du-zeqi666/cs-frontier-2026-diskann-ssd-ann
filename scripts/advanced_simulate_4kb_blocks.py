#!/usr/bin/env python3
"""
Trace-driven 4KB block locality simulation.

Assumptions (HARD-CODED in this script, must be declared in the report):
  - Each 4KB block holds B nodes (B in {4, 8, 16, 32, 64})
  - Original layout: block_id = node_id // B (sequential)
  - Reordered layout: greedy cluster by trace co-access frequency
  - NOT a real DiskANN index rewrite; only an upper-bound estimate

Trace format: 3-col TSV (qid event nid). Only miss+read events are used.
"""
import argparse
from collections import Counter, defaultdict


def read_trace_per_query(trace_path):
    """Return list of sets: per-query visited node sets."""
    per_q = []
    cur_qid = None
    cur_set = None
    with open(trace_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            qid_str, event, nid_str = parts
            if event not in ("miss", "read"):
                continue
            qid = int(qid_str)
            nid = int(nid_str)
            if qid != cur_qid:
                if cur_set is not None:
                    per_q.append(cur_set)
                cur_qid = qid
                cur_set = set()
            cur_set.add(nid)
    if cur_set is not None:
        per_q.append(cur_set)
    return per_q


def build_coaccess(per_q):
    """Return Counter((min, max) -> weight)."""
    co = Counter()
    for nodes in per_q:
        sorted_nodes = sorted(nodes)
        for i in range(len(sorted_nodes)):
            for j in range(i + 1, len(sorted_nodes)):
                co[(sorted_nodes[i], sorted_nodes[j])] += 1
    return co


def orig_blocks(per_q, B):
    """For each query, return number of unique blocks under original layout."""
    out = []
    for nodes in per_q:
        s = set()
        for nid in nodes:
            s.add(nid // B)
        out.append(len(s))
    return out


def greedy_cluster_reorder(per_q, B, coaccess, top_pairs=10000):
    """Greedy reorder: pick top co-access pairs and merge their blocks.

    Simulates an "ideal" layout: nodes that frequently co-occur end up in same block.
    Returns per-query count of unique blocks after this hypothetical reorder.
    """
    # Build a graph of "block_id -> set of node_ids" then greedily merge
    # Simpler approach: use the top co-access pairs to build a co-occurrence assignment.
    # For tractability: assign each node to a target block via greedy co-association.
    all_nodes = set()
    for nodes in per_q:
        all_nodes |= nodes

    # First, build a union-find over node_ids based on co-access threshold
    # Greedy: process top pairs, if both endpoints are still in different "clusters", union them
    # A cluster's size limit is B (block capacity)
    parent = {n: n for n in all_nodes}
    size = {n: 1 for n in all_nodes}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def can_union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if size[ra] + size[rb] > B:
            return False
        return True
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]

    # Greedy by top co-access weight
    merged_count = 0
    for (u, v), w in coaccess.most_common(top_pairs):
        if can_union(u, v):
            union(u, v)
            merged_count += 1
    # After clustering, assign each cluster to a virtual block
    # Then count per-query unique blocks via cluster_root
    out = []
    for nodes in per_q:
        s = set()
        for nid in nodes:
            s.add(find(nid))
        out.append(len(s))
    return out, merged_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", required=True)
    parser.add_argument("--B_list", nargs="+", type=int, default=[4, 8, 16, 32, 64])
    parser.add_argument("--out_csv", required=True)
    args = parser.parse_args()

    print(f"Reading trace: {args.trace}")
    per_q = read_trace_per_query(args.trace)
    print(f"  total queries: {len(per_q)}")
    total_nodes = set()
    for s in per_q:
        total_nodes |= s
    print(f"  unique nodes total: {len(total_nodes)}")

    print("Building co-access graph...")
    coaccess = build_coaccess(per_q)
    print(f"  co-access pairs: {len(coaccess)}")

    with open(args.out_csv, "w") as f:
        f.write("B,orig_unique_blocks_mean,reordered_unique_blocks_mean,compression_ratio,merged_pairs\n")
        for B in args.B_list:
            o = orig_blocks(per_q, B)
            r, merged = greedy_cluster_reorder(per_q, B, coaccess, top_pairs=max(20000, 5 * B * 1000))
            o_mean = sum(o) / max(len(o), 1)
            r_mean = sum(r) / max(len(r), 1)
            ratio = o_mean / max(r_mean, 1)
            f.write(f"{B},{o_mean:.2f},{r_mean:.2f},{ratio:.3f},{merged}\n")
            print(f"  B={B:3d}: orig={o_mean:7.2f}  reordered={r_mean:7.2f}  ratio={ratio:.3f}  merged={merged}")


if __name__ == "__main__":
    main()
