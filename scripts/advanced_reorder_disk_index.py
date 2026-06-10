#!/usr/bin/env python3
"""
Real 4KB block reorder tool for DiskANN (v3: trace-aware linear packing, fast).

Algorithm (much faster than v2's greedy):
  For each query (in trace order), take its 6 unassigned nodes and pack
  them into a sector. Falls back to "next unassigned" for queries with
  fewer than 6 unassigned nodes. This directly exploits per-query
  spatial locality (all nodes in a search are accessed together).
"""
import argparse
import os
import struct
import sys


SECTOR_LEN = 4096


def parse_trace_per_query(trace_path):
    per_q = []
    cur_qid, cur_set = None, None
    with open(trace_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            qid_s, ev, nid_s = parts
            if ev not in ("miss", "read"):
                continue
            try:
                qid, nid = int(qid_s), int(nid_s)
            except ValueError:
                continue
            if qid != cur_qid:
                if cur_set is not None:
                    per_q.append(cur_set)
                cur_qid, cur_set = qid, set()
            cur_set.add(nid)
    if cur_set is not None:
        per_q.append(cur_set)
    return per_q


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--index", required=True)
    p.add_argument("--trace", required=True)
    p.add_argument("--out_index", required=True)
    p.add_argument("--out_perm", required=True)
    p.add_argument("--nnodes", type=int, required=True)
    p.add_argument("--max_node_len", type=int, required=True)
    p.add_argument("--nnodes_per_sector", type=int, required=True)
    args = p.parse_args()

    n_sectors = (args.nnodes + args.nnodes_per_sector - 1) // args.nnodes_per_sector
    cap = args.nnodes_per_sector
    print(f"nnodes={args.nnodes}  cap={cap}  n_sectors={n_sectors}", flush=True)

    # Load entire original index
    print("Loading original index...", flush=True)
    with open(args.index, "rb") as f:
        orig_data = f.read()
    expected_size = SECTOR_LEN * (1 + n_sectors)
    assert len(orig_data) == expected_size, f"size {len(orig_data)} != {expected_size}"

    # Parse trace
    print("Parsing trace...", flush=True)
    per_q = parse_trace_per_query(args.trace)
    print(f"  {len(per_q)} queries", flush=True)

    # Per-query packing: for each query, put 6 unassigned nodes in next sector
    print("Per-query packing...", flush=True)
    sector_of_node = [-1] * args.nnodes
    placed = set()
    next_sector = 0
    cur_sector_nodes = []

    def finish_sector():
        nonlocal next_sector
        if not cur_sector_nodes:
            return
        for slot, nid in enumerate(cur_sector_nodes):
            sector_of_node[nid] = next_sector
        next_sector += 1
        cur_sector_nodes.clear()

    # Pass 1: per-query packing (in trace order)
    for q in per_q:
        unassigned_in_q = [nid for nid in q if nid not in placed]
        for nid in unassigned_in_q:
            if len(cur_sector_nodes) >= cap:
                finish_sector()
            if next_sector >= n_sectors:
                break
            cur_sector_nodes.append(nid)
            placed.add(nid)
        if next_sector >= n_sectors:
            break
    finish_sector()  # close last partial

    # Pass 2: fill remaining sectors with remaining unassigned nodes
    if next_sector < n_sectors:
        for nid in range(args.nnodes):
            if nid in placed:
                continue
            if len(cur_sector_nodes) >= cap:
                finish_sector()
            if next_sector >= n_sectors:
                break
            cur_sector_nodes.append(nid)
            placed.add(nid)
        finish_sector()

    n_placed = sum(1 for s in sector_of_node if s >= 0)
    print(f"  placed {n_placed}/{args.nnodes}", flush=True)
    assert n_placed == args.nnodes, f"only {n_placed} placed"

    # Build reordered index in memory
    # Layout: file sector 0 = header, file sectors 1..n_sectors = data
    # sector_of_node[i] in [0, n_sectors-1] is the DATA sector index
    # corresponding file sector = 1 + sector_of_node[i]
    print("Building reordered index...", flush=True)
    out = bytearray(expected_size)
    out[0:SECTOR_LEN] = orig_data[0:SECTOR_LEN]  # header
    # Pre-compute slot index per node
    slot_of = [0] * args.nnodes
    for sec in range(n_sectors):
        cnt = 0
        for nid in range(args.nnodes):
            if sector_of_node[nid] == sec:
                slot_of[nid] = cnt
                cnt += 1
    # Place each node at file sector (1 + sector_of_node[nid])
    for nid in range(args.nnodes):
        orig_off = (1 + nid // cap) * SECTOR_LEN + (nid % cap) * args.max_node_len
        node_bytes = orig_data[orig_off:orig_off + args.max_node_len]
        sec = sector_of_node[nid]
        new_off = (1 + sec) * SECTOR_LEN + slot_of[nid] * args.max_node_len
        out[new_off:new_off + args.max_node_len] = node_bytes

    # Write
    print(f"Writing {args.out_index}...", flush=True)
    with open(args.out_index, "wb") as f:
        f.write(out)
    print(f"  wrote {os.path.getsize(args.out_index)} B", flush=True)

    # Perm.bin: store LINEAR position (sector*cap + slot) so C++ can
    # recover both. get_node_sector = 1 + linear/cap, offset_to_node
    # uses linear%cap. This is needed because slot is no longer
    # = node_id % cap after co-access reorder.
    print(f"Writing {args.out_perm}...", flush=True)
    with open(args.out_perm, "wb") as f:
        for nid in range(args.nnodes):
            linear = sector_of_node[nid] * cap + slot_of[nid]
            f.write(struct.pack("<I", linear))
    print(f"  wrote {os.path.getsize(args.out_perm)} B", flush=True)

    # Verify
    print("Verifying 20 random nodes...", flush=True)
    import random
    random.seed(42)
    for nid in random.sample(range(args.nnodes), 20):
        orig_off = (1 + nid // cap) * SECTOR_LEN + (nid % cap) * args.max_node_len
        orig_bytes = orig_data[orig_off:orig_off + args.max_node_len]
        sec = sector_of_node[nid]
        new_off = (1 + sec) * SECTOR_LEN + slot_of[nid] * args.max_node_len
        new_bytes = out[new_off:new_off + args.max_node_len]
        assert orig_bytes == new_bytes, f"node {nid} mismatch!"
    print("  all 20 samples match ✓", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
