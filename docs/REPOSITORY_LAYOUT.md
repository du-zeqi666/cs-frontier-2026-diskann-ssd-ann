# Repository Layout

> 本仓库的目录结构与用途说明
> 生成时间: 2026-06-10
> 上游工作区: `/home/dzq/projects/DiskANN`(cpp_main @ 78256bba,含 v5.1 修改)
> 实验工作区: `/home/dzq/ann_exp/`

## 顶层目录

```
cs-frontier-2026-diskann-ssd-ann/
├── .git/                          Git 仓库(已存在,本整理未修改)
├── .gitignore                     排除 build/、__pycache__、.git/ 等
├── README.md                      项目说明 + 复现步骤 + 诚信声明
│
├── src/DiskANN/                   Microsoft DiskANN fork 源码快照
│                                  包含 v5.1 实验修改
│
├── patches/                       v5.1 增量 patch + v4 baseline patch + 备份
│
├── scripts/                       /home/dzq/ann_exp/scripts/ 完整镜像
│
├── results/                       所有实验产出
│   ├── csv/                       7 个聚合 CSV(便于查阅)
│   ├── raw/                       /home/dzq/ann_exp/result/ 完整镜像
│   ├── figures/                   /home/dzq/ann_exp/figures/ 完整镜像
│   ├── logs/                      /home/dzq/ann_exp/log/ 完整镜像
│                                (排除 v5 patch 与 backup_v4,这两项在 patches/)
│   └── docs/                      ADVANCED_EXPERIMENT_LOG.md + task3_bottleneck_summary.md
│
├── data/                          小型数据(可放 GitHub)
│   ├── random10k/                 3 个小文件(5.6 MB 总量)
│   └── sift1m_queries_groundtruth/  SIFT1M 查询与真值(不含 base.bin)
│
├── artifacts/                     实验产物(索引 + cache 列表)
│   ├── random10k_disk_index/      random10k 磁盘索引 8 个文件
│   └── cache_lists/               10 个 cache 节点列表 .txt
│
└── docs/                          仓库自身文档
    ├── REPOSITORY_LAYOUT.md       ← 本文件
    ├── LARGE_FILES_NOT_INCLUDED.md  跳过的大型文件清单
    ├── SOURCE_STATE.txt           v5.1 改动文件的 SHA256 与 patch 应用命令
    └── ai_logs/                    AI 对话记录(2 个合并文档,~812 KB)
```

> **关于实验报告（report）：** 本仓库**不包含**最终报告。报告 PDF / MD / LaTeX 源作为独立提交物存放在仓库外的 `../report/` 目录下，与代码仓库分离。如需阅读报告，请移步 `大作业/report/`。

## 各目录大小概览

| 目录 | 大小 | 文件数 | 说明 |
|---|---|---:|---|
| `src/DiskANN/` | ~5 MB | 562 | 不含 build/、__pycache__、嵌套 .git |
| `patches/` | ~91 KB | 6 | v5.1 patch 726 行 + v4 patch 545 行 + 4 个 v4 原始备份 |
| `scripts/` | 116 KB | 18 + 4 子目录 | 完整 Python 实验脚本集 |
| `results/csv/` | ~30 KB | 7 | 7 个聚合 CSV 汇总副本 |
| `results/raw/` | 17 MB | 57 顶层 + 5 子目录 | ann_exp/result/ 完整镜像(270 .bin + 8 .csv) |
| `results/figures/` | 2.3 MB | 1 .png + 5 子目录 | 15 张实验图(含 v5.1 新增 4 张) |
| `results/logs/` | 6.7 MB | 37 顶层 + 5 子目录 | 154 个 .log(基础 + 4 轮进阶) |
| `results/docs/` | ~28 KB | 2 | ADVANCED_EXPERIMENT_LOG.md + task3_bottleneck_summary.md |
| `data/random10k/` | 5.7 MB | 3 | base + query + gt |
| `data/sift1m_queries_groundtruth/` | 7 MB | 8 | 4 个 query + 4 个 gt |
| `artifacts/random10k_disk_index/` | 22 MB | 8 | disk.index + reordered + perm + PQ + sample |
| `artifacts/cache_lists/` | 510 KB | 10 | 1 个 BFS + 3 个 hot + 5 个 hybrid + 1 个 random10k |
| `docs/` | ~10 KB | 3 | 本目录 3 个 md |
| `docs/ai_logs/` | 812 KB | 2 | AI 对话合并文档(setup + plan/audit + chat logs) |

## 整理原则(本目录仅做复制,未修改任何实验文件)

1. 不得修改任何原始实验文件 — 全部 `cp -p` 保留时间戳与权限
2. 只能复制和整理,不得重写源码、脚本、CSV、日志、图片或报告
3. 不得重新生成实验结果 / 重新运行实验 / 重新应用 patch
4. 不得清理或删除原始工作区
5. 不得修改目标仓库现有的顶层 README.md
6. 不得覆盖现有 .git/
7. 不得复制任何嵌套 .git 目录或 .git 文件
8. 不得复制 DiskANN 的 build/
9. 不得复制完整 SIFT1M base 数据和大型 SIFT1M 索引
10. 不得编造 AI 使用记录
11. 不得自动执行 git commit / git push / git reset / git clean

## v5.1 改动文件位置(在 src/DiskANN/ 中)

| 文件 | 改动 |
|---|---|
| `src/DiskANN/src/pq_flash_index.cpp` | +281/-24 行(2 处改:`load_cache_list` 真 sector dedup,`cached_beam_search` frontier dedup + scratch 防御) |
| `src/DiskANN/include/percentile_stats.h` | +5 行(2 字段 `n_node_io_requests`, `n_unique_sectors`) |
| `src/DiskANN/include/pq_flash_index.h` | +23 行(`_block_aware_cache` 等 cache/perm 声明) |
| `src/DiskANN/apps/search_disk_index.cpp` | +121 行(per-query 打印 3 指标 + `--block_aware_cache` flag) |

如需对比 v4 → v5.1 增量:`patches/diskann_advanced_v5.1.patch` (726 行 git diff)
如需回滚到 v4:`patches/v4_baseline.patch` (545 行,反向) + `patches/backup_v4/` (4 个 v4 原始文件)