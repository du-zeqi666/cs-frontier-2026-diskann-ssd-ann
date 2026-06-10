# cs-frontier-2026-diskann-ssd-ann

> 南开大学 2026 春季学期「计算机系统前沿」(李雨森 / 崔立骁) 大作业 — 选题 2
> **基于 SSD 的向量检索优化**，研究方向为 Microsoft DiskANN 在 WSL2 Ubuntu-24.04 上的源码改造、性能评估与进阶优化。
>
> 学生：杜泽琦 (学号 2313508，信安 23 级)
> 上游 fork：`microsoft/DiskANN` 的 `cpp_main` 分支 @ commit `78256bba`
> 实验环境：WSL2 Ubuntu-24.04.2 LTS / 13th Gen Intel i5-13500H / 16 vCPU / 7.6 GB RAM / 1 TB NVMe
> 最终报告（PDF / LaTeX 源 / MD 源）：**位于仓库外的 `../report/` 下**，作为独立提交物，不在本仓库内

---

## 1. 项目说明

本仓库是课程大作业的**完整代码与实验数据备份**，包含：

- **源码 fork**：从 `microsoft/DiskANN@cpp_main@78256bba` 克隆，并叠加本人的 **v4 + v5.1 实验修改**（4 个文件 / 累计 +471/-51 行）
- **patches**：完整 v4 / v5.1 git diff patch + v4 原始代码备份，便于在干净 cpp_main 上重新应用或回滚
- **数据集**：random10k（5.7 MB 完整）+ SIFT1M 的 query / ground-truth（7 MB，**不含 488 MB 的 base**）
- **索引产物**：random10k 的原始 + v4 真实重排后的 disk.index（22 MB）
- **cache 列表**：10 个 BFS / hot / hybrid / random10k cache list
- **脚本**：21 个 Python 脚本（slice / trace / hot / hybrid / sim / reorder / aggregate / plot）
- **结果**：7 个聚合 CSV + 15 张 300 dpi 图 + 154 个 search / build 日志 + 2 个 markdown 总结
- **AI 对话记录**：`docs/ai_logs/` 下 2 个合并文档（setup 指南 + chat log + plan 审计，共 ~812 KB）
- **文档**：3 个 md / txt（仓库结构、跳过的大文件、v5.1 SHA256 与 patch 应用命令）

仓库大小 **~70 MB**（不含嵌套 `.git/` 与 DiskANN `build/`），适合 GitHub 直接推送。

---

## 2. 目录结构

```
cs-frontier-2026-diskann-ssd-ann/
├── README.md                      ← 本文件
├── .gitignore                     build / __pycache__ / .git 排除
│
├── src/DiskANN/                   Microsoft DiskANN fork 源码快照(已含 v5.1 改动)
├── patches/                       v5.1 patch + v4 baseline patch + v4 原始备份
├── scripts/                       全部 Python 实验脚本(21 个)
│
├── results/
│   ├── csv/                       7 个聚合 CSV
│   ├── raw/                       ann_exp/result/ 完整镜像(270 .bin + 8 .csv)
│   ├── figures/                   15 张实验图(基础 6 + 进阶 9)
│   ├── logs/                      154 个 search / build 日志
│   └── docs/                      ADVANCED_EXPERIMENT_LOG + bottleneck summary
│
├── data/
│   ├── random10k/                 random10k 完整数据集(5.7 MB)
│   └── sift1m_queries_groundtruth/  SIFT1M query + GT(7 MB,不含 488 MB base)
│
├── artifacts/
│   ├── random10k_disk_index/      原始 + v4 重排 disk.index(22 MB)
│   └── cache_lists/               10 个 BFS / hot / hybrid cache list(510 KB)
│
└── docs/
    ├── REPOSITORY_LAYOUT.md       本仓库目录结构与整理原则
    ├── LARGE_FILES_NOT_INCLUDED.md  跳过的大型文件清单(SIFT1M base、build/ 等)
    ├── SOURCE_STATE.txt           v5.1 改动文件 SHA256 + patch 应用命令
    └── ai_logs/                    AI 对话记录(2 个合并文档,~812 KB)
```

详细说明见 [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md)；跳过的大文件见 [`docs/LARGE_FILES_NOT_INCLUDED.md`](docs/LARGE_FILES_NOT_INCLUDED.md)。

---

## 3. 编译（从干净 cpp_main 复现 v5.1 状态）

> 本仓库 `src/DiskANN/` 已经处于 "cpp_main@78256bba + v5.1 修改" 的最终态。如果你 clone 后想验证修改是否完整，可以从干净 cpp_main 出发，用 `patches/` 下的 patch 重做：

```bash
# 1. 准备干净 cpp_main 工作区
mkdir ~/verify && cd ~/verify
git clone --recursive -b cpp_main https://github.com/microsoft/DiskANN.git
cd DiskANN
git checkout 78256bba

# 2. 校验 v4 baseline（这一步可选；跳过直接到 v5.1 也可）
git apply /path/to/cs-frontier-2026-diskann-ssd-ann/patches/v4_baseline.patch

# 3. 应用 v5.1 增量（最终态）
git apply /path/to/cs-frontier-2026-diskann-ssd-ann/patches/diskann_advanced_v5.1.patch

# 4. 编译
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
# 期望产物: apps/build_disk_index, build_memory_index, search_disk_index, search_memory_index
```

> ⚠️ 本仓库 `src/DiskANN/` **已经是最终态**，不要再 apply patch（否则会冲突）。

---

## 4. 实验复现

实验脚本都在 `scripts/` 下；日志在 `results/logs/` 下。具体复现步骤见仓库根目录下**最终报告**的"附录 C：可复现进阶实验的命令"。

简版流程：

```bash
# 1. 准备 random10k 数据（5.7 MB，已在 data/random10k/ 下）
mkdir -p ~/ann_exp/data
cp data/random10k/* ~/ann_exp/data/

# 2. 准备 SIFT1M query + GT（7 MB，已在 data/sift1m_queries_groundtruth/ 下）
cp data/sift1m_queries_groundtruth/* ~/ann_exp/data/sift1m/

# 3. SIFT1M base 需要单独从 http://corpus-texmex.irisa.fr/ 下载（168 MB → 488 MB .fvecs）

# 4. 跑基础实验（任务一/二/三）+ 进阶实验
# 命令列表见 ADVANCED_REPORT.md 与最终报告附录 C

# 5. 画图
cd scripts
python3 plot_basic_figures.py       # 6 张基础图
python3 plot_round2_figures_v2.py   # 3 张 v5.1 dedup 图
python3 plot_advanced_figures.py    # 7 张进阶 cache 图
```

完整复现指南见 `results/docs/ADVANCED_EXPERIMENT_LOG.md`（650+ 行实验日志）和报告附录 C（12 步）。

---

## 5. 数据诚信

**所有数字都来自本人实际跑出来的实验数据**，未经任何编造或 AI 推测：

- 基础任务（任务一/二/三）：`results/csv/task2_baseline_eval1000.csv`、`task3_disk_profile_eval1000.csv`、`task3_index_size_summary.csv`
- 进阶 cache 实验：`results/csv/advanced_all.csv`（39 行 × 27 字段）
- 进阶 4KB Block Locality：`results/csv/advanced_real_reorder.csv`（Round 2, 39 行）+ `advanced_real_reorder_v5.csv`（v5.1, 34 行）+ `block_sim.csv`（5 行）
- 原始日志：154 个 .log（基础 35 + 进阶 119），未做任何改写

未编造 AI 使用记录；所有 patch / 修改 / 限制都在源报告和 `docs/` 中如实记录。

---

## 6. v5.1 诚实声明（关键限制）

本实验在 v4 → v5.1 演进中主动识别并修复了 3 处 P0 假象，并在最终报告与本仓库中如实承认：

1. **v4 block-aware cache 是 per-node IO（假象）**：v4 报告 "1000 节点 BFS cache 在 C++ 层面被分组到 477 sectors"——这只是 sector 分组数，底层 libaio 仍提交 1000 个独立 4 KB read，**没有真正减少 IO**。**v5.1 修复**，cache load 阶段真实现 2.1× IO 压缩（52% dedup）。
2. **v4 prefetch-lite 是 CPU cache hint**：仅 x86 `PREFETCHT0/T1`，**不是 SSD 异步 IO**。真正的 `libaio io_submit` / `io_uring` **未实装**。因此**进阶 4（async IO / prefetch）不计入"完成项"**。
3. **v5.1 search frontier dedup 实现正确但无可观测信号**：random10k 图本身无 4 KB sector 局部性 + 全在 OS page cache + reorder 是 random permutation（不是 co-access 聚簇），所以 search 阶段 dedup 在 random10k 上仅 0–1% 差异（已在 `block_cache_actual_dedup.png` 与 `cache_load_dedup.png` 中如实展示）。

**未完成的进阶方向**：

- **进阶 1（RaBitQ 替换 PQ）**：未实装。涉及第三方库 + 距离函数重写，调试成本高，主动放弃。
- **进阶 4（Prefetch / 异步 IO）**：见上述 v5.1 诚实声明。

---

## 7. AI 使用边界

本课程大作业大量借助 AI 辅助（Claude Code 计划模式 + 执行模式），但本人对所有数据、代码、结论做了复核：

- **源码改动**（4 文件 +471/-51 行）：AI 设计并实装，本人在 DiskANN 官方 README 与原始日志上做了 correctness 验证（1000 query 跑出 38 158 trace 事件，3 列 TSV 完整）
- **21 个 Python 脚本**：AI 编写并执行，本人对脚本输出与原始 CSV 做了数值校验
- **154 组 search run + 5 组 block sim**：AI 在本地 DiskANN 编译产物上执行
- **15 张 300 dpi 图表**：AI 用 matplotlib 从 CSV 重绘，本人对关键数据点做了交叉验证
- **最终报告**：AI 基于本人实际跑出来的 CSV / PNG / 日志草拟，本人负责事实核对、诚实更正、文字润色

**结论：报告所有数字、所有结论都基于自己跑出来的数据；AI 仅作为工程加速器，不替代实际实验。**

---

## 8. License

- `src/DiskANN/`：继承上游 [MIT License](src/DiskANN/LICENSE)
- 其余内容（本人在本仓库新增的脚本、文档、配置）：未指定 License，仅用于课程评估

## 9. 联系

- 学生：杜泽琦（南开大学 密码与网络空间安全学院 信息安全 23 级）
- 课程：计算机系统前沿 (2026 春季)
- 任课教师：李雨森、崔立骁
- 提交时间：2026 春季学期末