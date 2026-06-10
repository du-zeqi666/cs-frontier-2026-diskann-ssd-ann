#!/usr/bin/env python3
"""
Build a frequency hot cache list from a Phase 1 trace file.

Trace format (3-col TSV, mandatory):
    qid  event  node_id
    event in {hit, miss, read}

Default: count only (miss, read) = nodes that actually triggered IO.
Use --include_hit to also count cache-hit nodes.

Output format: first line is total count, followed by one node_id per line.
This matches PQFlashIndex::load_cache_list(const string&) input format.
"""
import argparse
from collections import Counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", required=True)
    parser.add_argument("--k_list", nargs="+", type=int, required=True,
                        help="e.g. 3000 5000 10000")
    parser.add_argument("--events", nargs="+", default=["miss", "read"],
                        help="event types to count (default: miss read)")
    parser.add_argument("--include_hit", action="store_true",
                        help="also count 'hit' events")
    parser.add_argument("--out_prefix", required=True,
                        help="outputs go to {prefix}_k{K}.txt")
    args = parser.parse_args()

    if args.include_hit and "hit" not in args.events:
        args.events = list(args.events) + ["hit"]

    counter = Counter()
    n_lines = 0
    n_kept = 0
    with open(args.trace) as f:
        for line in f:
            n_lines += 1
            parts = line.strip().split()
            # STRICT 3-col parsing (no isdigit() to avoid L/W confusion)
            if len(parts) != 3:
                continue
            qid_str, event, nid_str = parts
            if event not in args.events:
                continue
            try:
                nid = int(nid_str)
            except ValueError:
                continue
            counter[nid] += 1
            n_kept += 1

    print(f"Trace lines: {n_lines}")
    print(f"Kept events ({args.events}): {n_kept}")
    print(f"Unique nodes: {len(counter)}")

    for k in args.k_list:
        topk = [nid for nid, _ in counter.most_common(k)]
        if len(topk) < k:
            print(f"  WARNING: requested {k} but only {len(topk)} unique nodes available")
        out_path = f"{args.out_prefix}_k{k}.txt"
        with open(out_path, "w") as f:
            f.write(f"{len(topk)}\n")
            for nid in topk:
                f.write(f"{nid}\n")
        print(f"  -> {out_path}  size={len(topk)}")


if __name__ == "__main__":
    main()
