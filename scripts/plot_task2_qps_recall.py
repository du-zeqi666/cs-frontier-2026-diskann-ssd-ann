import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

df = pd.read_csv(args.csv)
df["recall@10"] = pd.to_numeric(df["recall@10"], errors="coerce")
df["qps"] = pd.to_numeric(df["qps"], errors="coerce")
df = df.dropna(subset=["recall@10", "qps"])

plt.figure()
for method, g in df.groupby("method"):
    g = g.sort_values("recall@10")
    plt.plot(g["recall@10"], g["qps"], marker="o", label=method)

plt.xlabel("Recall@10")
plt.ylabel("QPS")
plt.title("QPS-Recall Curve on SIFT1M Eval1000")
plt.legend()
plt.grid(True)

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, dpi=200, bbox_inches="tight")
print(f"saved {out}")
