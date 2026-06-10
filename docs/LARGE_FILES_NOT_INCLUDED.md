# Large Files NOT Included

> 本仓库未包含的大型文件清单
> 整理规则:不复制 SIFT1M 原始大数据与大型 SIFT1M 索引(1 GB+)
> 时间: 2026-06-10

## 跳过的大型文件

### 1. SIFT1M 原始数据
来源: `/home/dzq/datasets/`

| 路径 | 大小 | 跳过原因 |
|---|---:|---|
| `sift.tar.gz` | 168 MB | SIFT1M 原始压缩包 |
| `sift/sift_base.fvecs` | 516 MB | SIFT1M 1M 节点原始基集 |
| `sift/sift_learn.fvecs` | 52 MB | SIFT1M learn 子集 |
| `sift/sift_query.fvecs` | 5 MB | SIFT1M query 原始 .fvecs |
| `sift/sift_groundtruth.ivecs` | 4 MB | SIFT1M 真值原始 .ivecs |

### 2. SIFT1M 转换后数据(在 ann_exp/data/)
| 路径 | 大小 | 跳过原因 |
|---|---:|---|
| `data/sift1m/sift_base.bin` | 488 MB | 488 MB 太大,仓库不适合 |

### 3. SIFT1M 内存索引(在 ann_exp/index/memory/)
| 路径 | 大小 | 跳过原因 |
|---|---:|---|
| `index/memory/sift1m_R32_L50.data` | ~450 MB | SIFT1M memory 索引太大 |
| `index/memory/sift1m_R32_L50` (无后缀) | 同上 | 重复文件 |
| `index/memory/random10k_R32_L50.data` | ~50 MB | 内存索引,可从 5MB base 数据快速重建 |
| `index/memory/random10k_R32_L50` (无后缀) | 同上 | 重复文件 |

### 4. SIFT1M 磁盘索引(在 ann_exp/index/disk/)
| 路径 | 大小 | 跳过原因 |
|---|---:|---|
| `sift1m_R32_L50_B1_M4_disk.index` | 682 MB | SIFT1M disk 索引太大 |
| `sift1m_R32_L50_B1_M4_pq_compressed.bin` | 128 MB | SIFT1M PQ 压缩数据 |
| `sift1m_R32_L50_B1_M4_sample_data.bin` | 51 MB | SIFT1M 样本数据 |
| `sift1m_R32_L50_B1_M4_sample_ids.bin` | 399 KB | SIFT1M 样本 ID(若需可单独复制,本整理跳过) |
| `sift1m_R32_L50_B1_M4_pq_pivots.bin` | 136 KB | 实际只 136 KB — 误判,见下 |

**注:** 实际本仓库**包含** `sift1m_R32_L50_B1_M4_pq_pivots.bin`(136 KB),因为它小不占空间。
其余 SIFT1M 索引文件确实跳过(>50 MB)。

### 5. DiskANN build/ 编译产物
来源: `/home/dzq/projects/DiskANN/build/`

| 路径 | 大小 | 跳过原因 |
|---|---:|---|
| `DiskANN/build/` | 144 MB | 编译产物,可从源码重建 |

### 6. 散落的 symlink
| 路径 | 跳过原因 |
|---|---|
| `/home/dzq/ann_exp/random10k_R32_L50_B1_M1_reordered_*.bin` (4 symlinks) | 是上面真实文件的软链接,放在顶层会重复 |

## 已包含的相关小型文件(为对照参考)

虽然 SIFT1M 大型文件未复制,但以下小文件**已包含**在仓库中:

### random10k 完整数据集(5.7 MB)
- `data/random10k/random10k_base.fbin` (5 MB)
- `data/random10k/random10k_query.fbin` (512 KB)
- `data/random10k/random10k_gt` (80 KB)

### SIFT1M 查询与真值(7 MB,不含 base)
- `data/sift1m_queries_groundtruth/sift_query.bin` (5 MB)
- `data/sift1m_queries_groundtruth/sift_query_eval{1000,800,profile200}.{bin,fbin}` (1 MB)
- `data/sift1m_queries_groundtruth/sift_gt_{eval1000,eval800,profile200,full}` (1 MB)

### random10k 磁盘索引与重排产物(22 MB)
- `artifacts/random10k_disk_index/random10k_R32_L50_B1_M1_disk.index` (6.8 MB)
- `artifacts/random10k_disk_index/random10k_R32_L50_B1_M1_disk.index.orig` (6.8 MB,改写前备份)
- `artifacts/random10k_disk_index/random10k_R32_L50_B1_M1_reordered_disk.index` (6.8 MB,v4 真实重排)
- `artifacts/random10k_disk_index/random10k_R32_L50_B1_M1_reordered_disk_perm.bin` (40 KB)
- `artifacts/random10k_disk_index/random10k_R32_L50_B1_M1_pq_*.bin` (1.4 MB)
- `artifacts/random10k_disk_index/random10k_R32_L50_B1_M1_sample_*.bin` (520 KB)

### Cache 节点列表(510 KB)
- `artifacts/cache_lists/bfs_cache_k10000.txt` (68 KB,SIFT1M 1 万节点 BFS)
- `artifacts/cache_lists/hot_cache_k{3000,5000,10000}.txt` (各 20-68 KB)
- `artifacts/cache_lists/hybrid_a{00,03,05,07,10}_k10000.txt` (各 68 KB)
- `artifacts/cache_lists/random10k_bfs_k1000.txt` (5 KB,random10k 1000 节点 BFS)

## 总结

| 类别 | 跳过大小 | 已包含大小 |
|---|---:|---:|
| SIFT1M 原始数据 | 745 MB | — |
| SIFT1M 转换数据(base) | 488 MB | — |
| SIFT1M 索引 | ~ 860 MB | 136 KB(pq_pivots.bin) |
| random10k 内存索引 | ~ 100 MB | — |
| SIFT1M 内存索引 | ~ 900 MB | — |
| DiskANN build/ | 144 MB | — |
| **跳过合计** | **~ 3.2 GB** | — |
| **已包含的对应小数据/索引** | — | **~ 30 MB** |

总体判断:仓库大小可控,便于 GitHub 推送与本地复现。
