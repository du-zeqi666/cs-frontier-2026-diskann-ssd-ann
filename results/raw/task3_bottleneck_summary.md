# Task 3 Profile Summary: DiskANN SSD Bottleneck Analysis

## Dataset and setting

- Dataset: SIFT1M with eval1000 queries
- Compared methods: Memory Vamana and DiskANN SSD
- Threads: 4
- DiskANN SSD beamwidth: 2
- DiskANN SSD cache nodes: 0
- Search list L: 10, 20, 40, 80, 120

## Main observations

- Memory Vamana average max RSS: 687.63 MB
- DiskANN SSD average max RSS: 151.78 MB
- Memory index total size: 592.16 MB
- Disk index total size: 822.37 MB
- DiskANN SSD average IO time ratio: 95.05%
- DiskANN SSD mean IOs range: 21.67 to 128.18
- Memory Vamana mean latency range: 94.73 us to 425.19 us
- DiskANN SSD mean latency range: 2532.73 us to 14196.55 us

## Per-L disk profile

| L | Recall@10 | QPS | Mean Latency us | Mean IOs | Mean IO us | IO Time Ratio % | Non-IO Ratio % | Max RSS MB |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 76.68 | 1558.99 | 2532.73 | 21.67 | 2412.35 | 95.25 | 4.75 | 153.1 |
| 20 | 86.63 | 1120.15 | 3534.84 | 31.01 | 3372.82 | 95.42 | 4.58 | 151.22 |
| 40 | 93.59 | 704.6 | 5629.14 | 49.79 | 5343.87 | 94.93 | 5.07 | 150.96 |
| 80 | 97.69 | 375.5 | 10595.22 | 88.73 | 10032.84 | 94.69 | 5.31 | 152.75 |
| 120 | 98.69 | 280.24 | 14196.55 | 128.18 | 13479.71 | 94.95 | 5.05 | 150.88 |

## Interpretation

As L increases, recall improves because the search explores more candidates, but DiskANN SSD performs more random IOs per query. This increases mean latency and reduces QPS.

The IO time ratio of DiskANN SSD is around 95% in the current experiment. Therefore, the main bottleneck is SSD random IO rather than pure CPU computation.

Compared with Memory Vamana, DiskANN SSD uses much less DRAM during search, but it pays the cost of SSD access latency. This explains why DiskANN SSD is slower while being more suitable for large-scale datasets that cannot fit entirely in memory.

## Note on vector computation time

The current DiskANN log directly reports mean IO time and mean latency, but it does not separately expose exact vector distance computation time. Therefore, this summary uses non-IO time, calculated as mean latency minus mean IO time, as an approximate upper bound for CPU-side work including vector distance computation, queue maintenance, and scheduling overhead.

## Conclusion

The profile results show that DiskANN SSD is mainly bottlenecked by random SSD IO. A natural optimization direction is to reduce SSD reads by caching frequently visited nodes or improving graph access locality.
