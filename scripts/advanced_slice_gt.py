#!/usr/bin/env python3
"""
Slice an .ibin ground-truth file into profile200 / eval800 subsets.
Format: header = (uint32 npoints, uint32 K) + npoints*K uint32.
Default splits (advanced experiment): profile200 = first 200, eval800 = last 800.
Must be called with the SAME --splits as advanced_slice_query.py so that
ground-truth rows stay aligned with query rows (CRITICAL: recall corruption otherwise).
"""
import argparse
import struct


def read_ibin(path):
    with open(path, "rb") as f:
        n, k = struct.unpack("II", f.read(8))
        data = f.read(n * k * 4)
    return n, k, data


def write_ibin(path, n, k, data):
    with open(path, "wb") as f:
        f.write(struct.pack("II", n, k))
        f.write(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output_prefix", required=True)
    parser.add_argument("--splits", nargs="+", required=True,
                        help="e.g. profile200:0:200 eval800:200:800")
    args = parser.parse_args()

    n, k, data = read_ibin(args.input)
    print(f"Input: {args.input}  npoints={n}  K={k}  size={len(data)} bytes")
    assert len(data) == n * k * 4, "File size mismatch with header"

    for spec in args.splits:
        name, s, e = spec.split(":")
        s = int(s); e = int(e)
        sub_n = e - s
        sub_data = data[s * k * 4 : e * k * 4]
        out_path = f"{args.output_prefix}_{name}"
        write_ibin(out_path, sub_n, k, sub_data)
        print(f"  -> {out_path}  npoints={sub_n}  K={k}  ({len(sub_data)} bytes)")


if __name__ == "__main__":
    main()
