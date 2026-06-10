import argparse
import struct
import numpy as np
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--count", type=int, required=True)
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.output)

    with inp.open("rb") as f:
        n, d = struct.unpack("II", f.read(8))
        data = np.fromfile(f, dtype=np.float32, count=n * d).reshape(n, d)

    s = args.start
    e = min(args.start + args.count, n)
    if s < 0 or s >= n:
        raise ValueError(f"start out of range: start={s}, n={n}")

    sub = data[s:e].copy()
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("wb") as f:
        f.write(struct.pack("II", sub.shape[0], sub.shape[1]))
        sub.astype(np.float32).tofile(f)

    print(f"input={inp}, n={n}, d={d}")
    print(f"output={out}, n={sub.shape[0]}, d={sub.shape[1]}")

if __name__ == "__main__":
    main()
