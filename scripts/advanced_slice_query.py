#!/usr/bin/env python3
"""
Slice a .fbin query file into profile200 / eval800 subsets.
Format: header = (uint32 npoints, uint32 ndim) + npoints*ndim float32.
Default splits (advanced experiment): profile200 = first 200, eval800 = last 800.
"""
import argparse
import struct
import os
import sys


def read_fbin(path):
    with open(path, "rb") as f:
        n, d = struct.unpack("II", f.read(8))
        data = f.read(n * d * 4)
    return n, d, data


def write_fbin(path, n, d, data):
    with open(path, "wb") as f:
        f.write(struct.pack("II", n, d))
        f.write(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output_prefix", required=True,
                        help="Output files will be {prefix}_{name}.fbin")
    parser.add_argument("--splits", nargs="+", required=True,
                        help="e.g. profile200:0:200 eval800:200:800")
    args = parser.parse_args()

    n, d, data = read_fbin(args.input)
    print(f"Input: {args.input}  npoints={n}  ndim={d}  size={len(data)} bytes")
    assert len(data) == n * d * 4, "File size mismatch with header"

    for spec in args.splits:
        name, s, e = spec.split(":")
        s = int(s); e = int(e)
        sub_n = e - s
        sub_data = data[s * d * 4 : e * d * 4]
        out_path = f"{args.output_prefix}_{name}.fbin"
        write_fbin(out_path, sub_n, d, sub_data)
        print(f"  -> {out_path}  npoints={sub_n}  ndim={d}  ({len(sub_data)} bytes)")


if __name__ == "__main__":
    main()
