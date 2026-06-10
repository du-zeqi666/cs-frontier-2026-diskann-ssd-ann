#!/usr/bin/env python3
"""
Run a batch of search_disk_index experiments with shared config.
Designed for Phase 3 baseline / Phase 4 hot / Phase 5 hybrid / Phase 7 beamwidth.
"""
import argparse
import os
import subprocess
import sys
import time


def run_one(binary, args_list, log_path):
    """Run one search_disk_index invocation, tee stdout/stderr to log_path."""
    cmd = [binary] + args_list
    print(f"[{time.strftime('%H:%M:%S')}] Running: {' '.join(cmd[:6])} ... -> {log_path}")
    with open(log_path, "w") as f:
        proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    return proc.returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, help="path to search_disk_index")
    parser.add_argument("--index", required=True)
    parser.add_argument("--query", required=True, help="query .fbin")
    parser.add_argument("--gt", required=True)
    parser.add_argument("--out_dir", required=True, help="where *_idx_uint32.bin goes")
    parser.add_argument("--log_dir", required=True, help="where raw logs go")
    parser.add_argument("--L_list", nargs="+", type=int, required=True)
    parser.add_argument("--W", type=int, default=4)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--K", type=int, default=10)
    parser.add_argument("--cache_list_in", default="")
    parser.add_argument("--cache_nodes", type=int, default=0)
    parser.add_argument("--label", default="run", help="log/result label prefix")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    for L in args.L_list:
        cli = [
            "--data_type", "float",
            "--dist_fn", "l2",
            "--index_path_prefix", args.index,
            "--query_file", args.query,
            "--gt_file", args.gt,
            "--recall_at", str(args.K),
            "--search_list", str(L),
            "--beamwidth", str(args.W),
            "--num_nodes_to_cache", str(args.cache_nodes),
            "--num_threads", str(args.threads),
        ]
        if args.cache_list_in:
            cli += ["--cache_list_in", args.cache_list_in]
        result_prefix = os.path.join(args.out_dir, f"{args.label}_L{L}")
        log_path = os.path.join(args.log_dir, f"{args.label}_L{L}.log")
        cli += ["--result_path", result_prefix]
        rc = run_one(args.binary, cli, log_path)
        print(f"  -> exit code: {rc}")


if __name__ == "__main__":
    main()
