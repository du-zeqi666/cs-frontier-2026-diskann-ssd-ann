# Setup & Execution Reference

> Consolidated reference for **WSL2 + DiskANN environment setup and command execution**.
> Distilled from 5 source documents in `reference/AI文档/`.
> Generated: 2026-06-10

## Table of Contents

1. [WSL2 Introduction & D-Drive Migration](#1-wsl2-introduction--d-drive-migration)
2. [WSL2 + DiskANN Cheat Sheet](#2-wsl2--diskann-cheat-sheet)
3. [Basic Task Full Command Playbook](#3-basic-task-full-command-playbook)
4. [Task 2 (SIFT1M Baseline) Detailed Commands](#4-task-2-sift1m-baseline-detailed-commands)
5. [Continuation Manual (After Smoke Test)](#5-continuation-manual-after-smoke-test)

---

## 1. WSL2 Introduction & D-Drive Migration

> Source: `WSL2_入门与迁移D盘详细手册.md` (1,580 lines, 25 KB)

# WSL2 入门与迁移 D 盘详细手册

> 整理日期：2026-06-07  
> 适用对象：准备在 Windows 笔记本上使用 WSL2 + Ubuntu-24.04 做课程大作业，尤其是“选题二：基于 SSD 的向量检索优化 / DiskANN”。  
> 当前电脑情况参考：  
> - WSL 发行版：`Ubuntu-24.04`  
> - WSL 版本：2  
> - 原 C 盘空间较紧张，后续将 WSL 迁移到 D 盘  
> - 推荐工作目录：`/home/dzq`、`~/projects`、`~/datasets`、`~/ann_exp`

---

## 1. 为什么要用 WSL2

WSL 是 Windows Subsystem for Linux，简单说就是在 Windows 里运行 Linux 环境。

做 DiskANN 这类系统实验时，推荐使用 WSL2，而不是直接在 Windows 上硬装各种依赖，原因是：

1. DiskANN、CMake、gcc/g++、Linux IO 工具在 Ubuntu 下更自然；
2. 实验脚本、编译环境更接近课程和开源项目说明；
3. 不需要重装系统；
4. 比完整虚拟机轻便；
5. 对你的选题二来说，不需要 GPU，重点是 CPU、内存和 SSD IO。

但是要注意：WSL2 虽然好用，但 DiskANN 的代码、数据集、索引文件最好放在 WSL 内部 Linux 文件系统里，而不是 Windows 挂载目录。

推荐：

```bash
~/projects
~/datasets
~/ann_exp
```

不推荐：

```bash
/mnt/c/Users/Dzq
/mnt/d/...
```

---

## 2. 选题二对电脑的基本要求

选题二主要做的是：

- 编译 DiskANN；
- 下载或准备向量数据集；
- 构建内存索引或 SSD 索引；
- 做 QPS、Recall、IO、延迟等实验；
- 如果做进阶，可以修改 cache 策略。

它主要吃：

| 资源 | 影响 |
|---|---|
| CPU | 构建索引、查询实验会占 CPU |
| 内存 | 数据集和索引构建阶段会占内存 |
| SSD 空间 | 数据集、索引、中间文件都占空间 |
| SSD 随机 IO | DiskANN SSD 版的瓶颈通常与随机 IO 有关 |
| GPU | 基本不需要 |

建议配置：

| 实验规模 | 建议 |
|---|---|
| 10K / 100K 调试 | 5GB - 10GB 空间即可 |
| 500K 实验 | 15GB - 30GB 更稳 |
| SIFT1M 正式实验 | 建议 30GB - 50GB 以上 |
| 10M 数据集 | 不建议一开始做 |

你的情况中，C 盘只剩大约 24GB，D 盘剩余更多，因此推荐将 WSL 整体迁移到 D 盘。

---

## 3. 判断电脑是否已有 WSL2

打开 Windows PowerShell，执行：

```powershell
wsl -l -v
```

你看到过类似结果：

```text
NAME              STATE           VERSION
* Ubuntu-24.04    Stopped         2
  docker-desktop  Stopped         2
```

说明：

- 已经安装了 WSL；
- `Ubuntu-24.04` 是你的 Ubuntu 发行版；
- `VERSION 2` 表示它是 WSL2；
- 星号 `*` 表示默认发行版。

如果默认是 `docker-desktop`，可以改成 Ubuntu：

```powershell
wsl --set-default Ubuntu-24.04
```

再次检查：

```powershell
wsl -l -v
```

希望看到：

```text
* Ubuntu-24.04      Stopped         2
  docker-desktop    Stopped         2
```

---

## 4. 如果还没安装 WSL2，可以怎么装

如果电脑还没有 WSL，可以在 PowerShell 管理员模式中执行：

```powershell
wsl --install
```

也可以指定 Ubuntu 版本：

```powershell
wsl --install -d Ubuntu-24.04
```

安装后重启电脑，再执行：

```powershell
wsl -l -v
```

如果看到 `VERSION 2`，说明是 WSL2。

如果不是 WSL2，可以尝试设置默认版本：

```powershell
wsl --set-default-version 2
```

如果系统提示虚拟化没有开启，需要进入 BIOS/UEFI 开启 CPU Virtualization / SVM / VT-x。一般新电脑默认是开启的。

---

## 5. 查看 Windows 各盘剩余空间

PowerShell 执行：

```powershell
Get-PSDrive -PSProvider FileSystem
```

你之前看到的是：

```text
Name           Used (GB)     Free (GB) Provider      Root
----           ---------     --------- --------      ----
C                 175.95         24.05 FileSystem    C:\
D                 398.16         60.51 FileSystem    D:\
E                 276.88         16.09 FileSystem    E:\
```

结论：

- C 盘只剩 24GB，不适合继续放 WSL 实验环境；
- D 盘剩 60GB，相对更适合；
- E 盘剩 16GB，也不够宽裕。

如果在 CMD 中输入 `Get-PSDrive` 报错：

```text
'Get-PSDrive' 不是内部或外部命令
```

说明你在 CMD 里，而不是 PowerShell。解决方法是打开 PowerShell，或者在 CMD 中执行：

```cmd
powershell -NoProfile -Command "Get-PSDrive -PSProvider FileSystem"
```

---

## 6. 为什么要看 WSL 安装位置

WSL2 的 Linux 文件系统通常存在一个虚拟磁盘文件中：

```text
ext4.vhdx
```

如果 WSL 默认装在 C 盘，那么你后续在 Linux 里下载数据集、编译代码、生成索引，底层都会不断增大 C 盘里的 `ext4.vhdx`。

这会带来风险：

1. C 盘被撑满；
2. Windows 系统变慢；
3. 实验中途失败；
4. 数据集或索引文件没空间写入；
5. 后续清理麻烦。

所以硬盘不够时，建议一开始就把 WSL 整体迁移到空间更大的盘，比如 D 盘。

---

## 7. 查找 ext4.vhdx

可以尝试：

```powershell
Get-ChildItem -Path $env:LOCALAPPDATA\Packages -Recurse -Filter ext4.vhdx -ErrorAction SilentlyContinue |
Select-Object FullName,@{Name="SizeGB";Expression={[math]::Round($_.Length/1GB,2)}}
```

如果没搜出来，不一定是失败。可能原因：

1. Ubuntu 很干净，还没生成很大的虚拟磁盘；
2. WSL 不是 Store 包路径；
3. 已经通过其他方式安装；
4. 权限或路径原因没有搜到。

你后面通过 `wsl --export` / `wsl --import` 的方式迁移到了 D 盘，所以最重要的是迁移后检查：

```powershell
dir D:\WSL\Ubuntu-24.04
```

看到：

```text
ext4.vhdx
```

就说明迁移位置正确。

---

## 8. WSL 迁移到 D 盘的完整步骤

### 8.1 总体思路

迁移不是简单复制文件夹，而是：

1. 关闭 WSL；
2. 把当前 Ubuntu 导出成 `.tar` 备份；
3. 确认备份存在；
4. 注销原来的 Ubuntu；
5. 从 `.tar` 导入到 D 盘指定目录；
6. 设置默认发行版；
7. 进入并检查；
8. 确认没问题后删除备份包。

---

### 8.2 关闭 WSL

PowerShell：

```powershell
wsl --shutdown
```

---

### 8.3 创建 D 盘目录

```powershell
mkdir D:\WSL
mkdir D:\WSL\backup
mkdir D:\WSL\Ubuntu-24.04
```

目录含义：

| 目录 | 作用 |
|---|---|
| `D:\WSL` | WSL 总目录 |
| `D:\WSL\backup` | 临时放导出的 tar 备份 |
| `D:\WSL\Ubuntu-24.04` | 迁移后 Ubuntu 的实际位置 |

---

### 8.4 导出当前 Ubuntu

```powershell
wsl --export Ubuntu-24.04 D:\WSL\backup\Ubuntu-24.04.tar
```

你曾经看到过类似输出：

```text
正在导出，这可能需要几分钟时间。 (75 MB)
wsl: 出现了内部错误。
错误代码: CreateVm/ConfigureNetworking/0x8007054f
wsl: 无法配置网络 (networkingMode Mirrored)，回退到 networkingMode None。
操作成功完成。
```

这里重点是最后一句：

```text
操作成功完成。
```

只要它出现，通常导出是成功的。前面的网络警告不是导出失败。

---

### 8.5 确认备份文件存在

```powershell
dir D:\WSL\backup
```

你看到过类似：

```text
-a----  2026/6/7  16:34  80660480  Ubuntu-24.04.tar
```

这说明备份 tar 文件已经存在。

---

### 8.6 注销原来的 Ubuntu

注意：这一步会删除原来的 WSL 发行版，所以必须先确认 `.tar` 备份存在。

```powershell
wsl --unregister Ubuntu-24.04
```

看到：

```text
正在注销。
操作成功完成。
```

说明注销完成。

---

### 8.7 从 D 盘重新导入

```powershell
wsl --import Ubuntu-24.04 D:\WSL\Ubuntu-24.04 D:\WSL\backup\Ubuntu-24.04.tar --version 2
```

你曾经看到过：

```text
错误代码: RegisterDistro/CreateVm/ConfigureNetworking/0x8007054f
wsl: 无法配置网络 (networkingMode Mirrored)，回退到 networkingMode None。
操作成功完成。
```

仍然是看最后一句：

```text
操作成功完成。
```

说明导入成功。

---

### 8.8 检查 WSL 列表

```powershell
wsl -l -v
```

期望结果：

```text
NAME              STATE           VERSION
* Ubuntu-24.04    Stopped         2
  docker-desktop  Stopped         2
```

如果星号不在 Ubuntu 上，执行：

```powershell
wsl --set-default Ubuntu-24.04
```

---

### 8.9 检查 D 盘目录

```powershell
dir D:\WSL\Ubuntu-24.04
```

看到：

```text
ext4.vhdx
```

说明新的 Ubuntu 虚拟磁盘已经在 D 盘。

你当时看到过：

```text
D:\WSL\Ubuntu-24.04\ext4.vhdx
```

这就说明迁移成功。

---

### 8.10 进入新的 WSL

```powershell
wsl -d Ubuntu-24.04
```

如果进入后看到类似：

```bash
root@LAPTOP-QPEUU9JO:/mnt/c/Users/Dzq#
```

说明已经进入 WSL 了。虽然有网络警告，但不是进不去。

---

## 9. 处理 WSL 网络警告

### 9.1 问题现象

你之前出现过：

```text
wsl: 无法配置网络 (networkingMode Mirrored)，回退到 networkingMode None。
wsl: 检测到 localhost 代理配置，但未镜像到 WSL。NAT 模式下的 WSL 不支持 localhost 代理。
```

通常原因是用户目录下的 `.wslconfig` 中配置了 `networkingMode=mirrored`，但当前系统环境不支持或配置不完整。

---

### 9.2 修改 .wslconfig

PowerShell 执行：

```powershell
notepad $env:USERPROFILE\.wslconfig
```

推荐写成：

```ini
[wsl2]
networkingMode=NAT
autoProxy=false
```

保存后，关闭记事本。

然后：

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

如果仍然有 localhost 代理提示，但 `apt update` 能运行，一般可以先不管。

---

## 10. 进入 WSL 后为什么会在 /mnt/c/Users/Dzq

你进入 WSL 后曾经看到：

```bash
dzq@LAPTOP-QPEUU9JO:/mnt/c/Users/Dzq$
```

这不是 WSL 没迁移成功，而是因为你是从 Windows 的：

```text
C:\Users\Dzq
```

启动的 WSL。WSL 会默认从当前 Windows 目录映射过去。

解决方法很简单：

```bash
cd ~
pwd
```

如果看到：

```bash
/home/dzq
```

就对了。

以后每次进入 WSL 后，先做：

```bash
cd ~
```

或者直接在 WSL 终端里打开 Ubuntu，不要从 C 盘目录开始操作。

---

## 11. root 用户和普通用户

### 11.1 为什么不建议长期用 root

`root` 是 Linux 超级管理员。它可以执行任何操作，包括误删系统目录。所以日常编译、下载、实验最好用普通用户，比如：

```text
dzq
```

需要管理员权限时再用：

```bash
sudo
```

---

### 11.2 导入 WSL 后默认变 root 的原因

通过：

```powershell
wsl --import
```

导入的 WSL，经常默认用户会变成 root。这是正常现象，不是错误。

---

## 12. 创建普通用户 dzq

如果当前是 root：

```bash
whoami
```

输出：

```text
root
```

先切到家目录：

```bash
cd ~
pwd
```

如果系统太精简，`adduser` 可能不存在。先安装：

```bash
apt update
apt install -y adduser sudo passwd
```

如果 `apt update` 曾经部分失败，但后面又能下载软件包，一般可以继续。

创建用户：

```bash
adduser dzq
```

它会让你输入密码：

```text
New password:
Retype new password:
```

后面的信息可以一路回车：

```text
Full Name []
Room Number []
Work Phone []
Home Phone []
Other []
```

最后确认：

```text
Is the information correct? [Y/n] y
```

---

## 13. 给 dzq 加 sudo 权限

root 下执行：

```bash
usermod -aG sudo dzq
```

检查：

```bash
groups dzq
```

希望看到：

```text
dzq : dzq users sudo
```

如果没加成功，普通用户执行 `sudo apt update` 会出现：

```text
dzq is not in the sudoers file.
```

这种情况需要重新用 root 进入：

```powershell
wsl -d Ubuntu-24.04 -u root
```

然后：

```bash
usermod -aG sudo dzq
```

---

## 14. 设置默认用户为 dzq

root 下执行：

```bash
cat > /etc/wsl.conf <<EOF
[user]
default=dzq
EOF
```

退出：

```bash
exit
```

回到 PowerShell：

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

检查：

```bash
whoami
pwd
```

希望看到：

```text
dzq
/home/dzq
```

如果看到：

```text
dzq
/mnt/c/Users/Dzq
```

也没问题，执行：

```bash
cd ~
pwd
```

即可回到：

```text
/home/dzq
```

---

## 15. sudo 修复过程复盘

你之前遇到：

```text
dzq is not in the sudoers file.
```

修复流程是：

1. 退出 WSL；
2. PowerShell 用 root 进入；
3. root 执行 `usermod -aG sudo dzq`；
4. 退出；
5. `wsl --shutdown`；
6. 重新进入；
7. 检查 `groups`；
8. 再执行 `sudo apt update`。

完整命令：

```powershell
wsl -d Ubuntu-24.04 -u root
```

root 中：

```bash
usermod -aG sudo dzq
groups dzq
exit
```

PowerShell：

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

WSL 中：

```bash
whoami
groups
sudo apt update
```

你最终看到：

```text
dzq
dzq sudo users
```

说明 sudo 修好了。

---

## 16. 检查 WSL 磁盘空间

WSL 中执行：

```bash
df -h ~
```

你看到过：

```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdd       1007G  386M  956G   1% /
```

这说明：

- WSL 内部文件系统显示约 1TB；
- 当前只用了很少；
- 可用空间充足；
- 做 DiskANN 实验空间上比原 C 盘安全很多。

注意：这不代表 D 盘真的凭空多了 1TB。WSL 的 `ext4.vhdx` 是动态增长的虚拟磁盘文件，实际占用会随着你下载数据集、编译代码、生成索引而增大。

所以仍然要关注 Windows D 盘剩余空间：

```powershell
Get-PSDrive -PSProvider FileSystem
```

---

## 17. 检查网络

基础测试：

```bash
ping -c 4 baidu.com
curl -I https://github.com
```

如果提示：

```text
ping: command not found
curl: command not found
```

说明系统太精简，安装即可：

```bash
sudo apt update
sudo apt install -y iputils-ping curl ca-certificates
```

如果 `baidu.com` 能通，GitHub 不通，说明基础网络可用，但 GitHub 访问不稳定。后续拉代码时可以重试、配置代理或使用镜像。

---

## 18. 更新 Ubuntu 软件包

先更新软件源：

```bash
sudo apt update
```

再升级软件包：

```bash
sudo apt upgrade -y
```

如果提示有若干包可以升级，例如：

```text
33 packages can be upgraded.
```

可以执行 `sudo apt upgrade -y`。

如果有某个源临时失败，例如：

```text
Temporary failure resolving 'security.ubuntu.com'
```

但其他源能下载，通常是 DNS 或网络临时问题。可以稍后重试。

---

## 19. 安装基础网络和开发工具

先安装最基础的网络工具：

```bash
sudo apt install -y iputils-ping curl ca-certificates
```

再安装编译工具：

```bash
sudo apt install -y \
  build-essential \
  gcc \
  g++ \
  gdb \
  cmake \
  make \
  ninja-build \
  git \
  pkg-config \
  wget \
  unzip \
  zip \
  tar \
  python3 \
  python3-pip \
  python3-venv
```

这些工具含义：

| 工具 | 作用 |
|---|---|
| `gcc/g++` | C/C++ 编译器 |
| `cmake` | 构建配置工具 |
| `make` | 编译执行工具 |
| `git` | 拉取代码 |
| `wget/curl` | 下载文件、测试网络 |
| `python3` | 跑实验脚本 |
| `python3-venv` | 创建 Python 虚拟环境 |
| `unzip/zip/tar` | 解压缩数据集或源码 |

---

## 20. 安装 DiskANN 常用依赖

```bash
sudo apt install -y \
  libaio-dev \
  libboost-all-dev \
  libtbb-dev \
  libomp-dev \
  libopenblas-dev \
  liblapack-dev \
  libgoogle-perftools-dev \
  libssl-dev \
  zlib1g-dev \
  htop \
  iotop \
  sysstat \
  time \
  fio \
  numactl
```

这些包大概作用：

| 包 | 作用 |
|---|---|
| `libaio-dev` | Linux 异步 IO，DiskANN 相关 |
| `libboost-all-dev` | Boost C++ 库 |
| `libtbb-dev` | 并行库 |
| `libomp-dev` | OpenMP |
| `libopenblas-dev` / `liblapack-dev` | 线性代数库 |
| `libgoogle-perftools-dev` | 性能工具 |
| `htop` | 看 CPU/内存 |
| `iotop` | 看 IO |
| `sysstat` | 提供 `iostat` |
| `fio` | 磁盘 IO 测试 |
| `numactl` | NUMA 相关工具 |

---

## 21. 安装 MKL 时如何选择

如果执行：

```bash
sudo apt install -y clang-format libmkl-full-dev
```

过程中出现：

```text
Use libmkl_rt.so as the default alternative to BLAS/LAPACK? [yes/no]
```

建议输入：

```text
no
```

原因：

- 你安装 MKL 主要是为了兼容 DiskANN 编译需求；
- 不需要把 MKL 设置为整个系统默认 BLAS/LAPACK；
- 选 `no` 更稳，不影响其他软件。

如果后面 DiskANN 编译真的找不到 MKL，再单独处理。

---

## 22. tzdata 时区配置

安装过程中可能出现：

```text
Configuring tzdata
Please select the geographic area in which you live.
```

选择：

```text
5
```

代表 Asia。

后面选择城市：

```text
Shanghai
```

如果不想交互选择，也可以之后执行：

```bash
sudo ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
sudo dpkg-reconfigure -f noninteractive tzdata
```

---

## 23. 检查编译环境

安装完成后检查：

```bash
gcc --version
g++ --version
cmake --version
git --version
python3 --version
```

你之前得到的结果：

```text
gcc 13.3.0
g++ 13.3.0
cmake 3.28.3
git 2.43.0
Python 3.12.3
```

这说明基础环境正常。

---

## 24. 创建实验目录

进入 Linux 家目录：

```bash
cd ~
pwd
```

确认：

```text
/home/dzq
```

创建目录：

```bash
mkdir -p ~/projects ~/datasets ~/ann_exp
mkdir -p ~/ann_exp/index ~/ann_exp/result ~/ann_exp/log ~/ann_exp/scripts
```

目录规划：

```text
/home/dzq
├── projects      # 放源码，例如 DiskANN
├── datasets      # 放数据集，例如 SIFT 子集
└── ann_exp
    ├── index     # 放索引
    ├── result    # 放实验结果
    ├── log       # 放日志和环境记录
    └── scripts   # 放脚本
```

---

## 25. 创建 Python 虚拟环境

```bash
cd ~/ann_exp
python3 -m venv venv
source ~/ann_exp/venv/bin/activate
pip install --upgrade pip
pip install numpy pandas matplotlib scipy tqdm h5py
```

测试：

```bash
python - << 'PY'
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
print("Python env OK")
PY
```

以后每次要用这个 Python 环境：

```bash
source ~/ann_exp/venv/bin/activate
```

退出环境：

```bash
deactivate
```

---

## 26. 记录实验环境

写报告时需要说明环境，因此建议一开始就保存：

```bash
mkdir -p ~/ann_exp/log

{
  echo "===== OS ====="
  lsb_release -a
  echo
  echo "===== Kernel ====="
  uname -a
  echo
  echo "===== CPU ====="
  lscpu
  echo
  echo "===== Memory ====="
  free -h
  echo
  echo "===== Disk ====="
  df -h
  echo
  echo "===== Compiler ====="
  gcc --version
  g++ --version
  cmake --version
} > ~/ann_exp/log/environment.txt
```

查看：

```bash
cat ~/ann_exp/log/environment.txt
```

这份文件后面可以直接放进报告或作为附录参考。

---

## 27. DiskANN 源码下载

建议使用 C++ 旧版分支：

```bash
cd ~/projects
git clone --recursive -b cpp_main https://github.com/microsoft/DiskANN.git
```

如果 GitHub 网络不好，可能会超时。可以先测试：

```bash
curl -I https://github.com
```

如果 `baidu.com` 能通而 GitHub 不通，说明 WSL 网络基本没问题，只是 GitHub 访问不稳定。可以：

1. 多试几次；
2. 使用代理；
3. 使用镜像；
4. 在浏览器下载 zip，再复制到 WSL 内部目录。

注意：如果从 Windows 下载了 zip，不要直接在 `/mnt/c` 里编译。可以复制到 WSL 内部：

```bash
cp /mnt/c/Users/Dzq/Downloads/DiskANN.zip ~/projects/
cd ~/projects
unzip DiskANN.zip
```

---

## 28. DiskANN 编译

进入源码目录：

```bash
cd ~/projects/DiskANN
```

创建构建目录：

```bash
mkdir -p build
cd build
```

配置：

```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
```

编译：

```bash
make -j$(nproc)
```

如果你想保存编译日志：

```bash
make -j$(nproc) 2>&1 | tee ~/ann_exp/log/diskann_build.log
```

查看最后报错：

```bash
tail -n 30 ~/ann_exp/log/diskann_build.log
```

编译成功后检查：

```bash
ls ~/projects/DiskANN/build/apps
```

希望看到类似：

```text
build_memory_index
search_memory_index
build_disk_index
search_disk_index
```

---

## 29. 为什么不要把实验放在 /mnt/c 或 /mnt/d

WSL 中：

```bash
/mnt/c
/mnt/d
```

是 Windows 文件系统挂载进来的路径。虽然能读写，但对 DiskANN 这种 SSD IO 实验不理想。

原因：

1. 跨文件系统访问可能更慢；
2. IO 延迟和 QPS 不稳定；
3. profile 出来的结果可能掺杂 Windows 文件系统开销；
4. 不利于比较原版 DiskANN 和你修改后的 cache 策略；
5. 报告中解释成本更高。

正确做法：

```bash
cd ~
mkdir -p ~/projects ~/datasets ~/ann_exp
```

虽然 WSL 底层虚拟磁盘在 D 盘，但在 Linux 里仍然使用 `/home/dzq/...`。这样既占用 D 盘空间，又保持 Linux 文件系统性能。

---

## 30. 实验规模建议

不要一开始就跑大数据。

推荐路线：

### 第一步：10K smoke test

目的：确认编译和流程能跑通。

关注：

- 能否构建索引；
- 能否搜索；
- 输出格式是否正常；
- 是否有权限或路径错误。

### 第二步：100K 调试

目的：开始看 QPS、Recall、参数变化。

关注：

- L 参数变化；
- QPS 是否下降；
- Recall 是否提升；
- 结果文件是否能画图。

### 第三步：500K 实验

目的：形成比较像样的实验数据。

关注：

- 内存版和 SSD 版差距；
- IO 次数；
- 平均延迟；
- cache 是否有效。

### 第四步：SIFT1M

目的：如果空间和时间够，可以作为正式实验规模。

注意：

- 索引文件会更大；
- 构建时间更长；
- SSD IO 更明显；
- 需要更规范地记录结果。

### 不建议：10M

不建议一开始做 10M，因为：

- 空间压力大；
- 构建时间长；
- 排错困难；
- 对课程作业来说性价比不高。

---

## 31. 报告中建议记录的环境信息

报告里可以写：

```text
系统：Windows + WSL2 Ubuntu-24.04
WSL 位置：D:\WSL\Ubuntu-24.04
工作目录：/home/dzq
CPU：用 lscpu 查看
内存：用 free -h 查看
磁盘：用 df -h 查看
编译器：gcc/g++ --version
CMake：cmake --version
Python：python3 --version
```

可以直接用：

```bash
cat ~/ann_exp/log/environment.txt
```

获取。

---

## 32. 常见问题复盘

### 32.1 `Get-PSDrive` 报错

原因：在 CMD 里执行了 PowerShell 命令。  
解决：打开 PowerShell。

---

### 32.2 `ext4.vhdx` 搜不到

不一定有问题。迁移后直接看：

```powershell
dir D:\WSL\Ubuntu-24.04
```

看到 `ext4.vhdx` 即可。

---

### 32.3 迁移时出现 networkingMode 报错

如果最后有：

```text
操作成功完成。
```

一般可以继续。

后续编辑：

```powershell
notepad $env:USERPROFILE\.wslconfig
```

写入：

```ini
[wsl2]
networkingMode=NAT
autoProxy=false
```

---

### 32.4 进入 WSL 后是 root

这是 `wsl --import` 后常见情况。创建普通用户并设置默认用户即可。

---

### 32.5 `adduser: command not found`

系统太精简，先安装：

```bash
apt update
apt install -y adduser sudo passwd
```

---

### 32.6 `dzq is not in the sudoers file`

用 root 进入：

```powershell
wsl -d Ubuntu-24.04 -u root
```

加组：

```bash
usermod -aG sudo dzq
```

重启 WSL。

---

### 32.7 `ping: command not found` / `curl: command not found`

安装：

```bash
sudo apt install -y iputils-ping curl ca-certificates
```

---

### 32.8 一进入就是 `/mnt/c/Users/Dzq`

执行：

```bash
cd ~
pwd
```

后续只要在 `/home/dzq` 下操作就可以。

---

## 33. 推荐的每日使用流程

以后每次开始做实验：

PowerShell：

```powershell
wsl -d Ubuntu-24.04
```

进入 WSL 后：

```bash
cd ~
pwd
```

确认：

```text
/home/dzq
```

激活 Python 环境：

```bash
source ~/ann_exp/venv/bin/activate
```

进入项目：

```bash
cd ~/projects/DiskANN
```

查看空间：

```bash
df -h ~
```

查看资源：

```bash
free -h
nproc
```

开始编译或跑实验。

---

## 34. 推荐的当前状态检查清单

你现在理想状态应该是：

```bash
whoami
```

输出：

```text
dzq
```

```bash
groups
```

输出包含：

```text
sudo
```

```bash
pwd
```

最好是：

```text
/home/dzq
```

```bash
df -h ~
```

显示空间充足。

```bash
gcc --version
g++ --version
cmake --version
git --version
python3 --version
```

都能正常输出。

```bash
sudo apt update
```

能正常更新。

如果这些都满足，就可以继续做 DiskANN 编译和实验。

---

## 35. 最重要的几个原则

1. **C 盘空间少时，不要把 WSL 留在 C 盘。**
2. **迁移 WSL 前必须先导出备份。**
3. **执行 `wsl --unregister` 前必须确认 `.tar` 备份存在。**
4. **进入 WSL 后先 `cd ~`。**
5. **代码、数据集、索引都放 `/home/dzq` 下。**
6. **不要在 `/mnt/c`、`/mnt/d` 跑正式 DiskANN 实验。**
7. **先跑小数据，再跑大数据。**
8. **所有对比实验必须在同一环境下跑。**
9. **报告中要记录系统、CPU、内存、磁盘、编译器、数据集和参数。**
10. **遇到报错保留最后 30 行日志，方便定位。**

---

## 2. WSL2 + DiskANN Cheat Sheet

> Source: `WSL2_DiskANN_常用指令速查.md` (1,000 lines, 14 KB)

# WSL2 + DiskANN 常用指令速查

> 整理日期：2026-06-07  
> 适用场景：Windows + WSL2 Ubuntu-24.04，准备做“选题二：基于 SSD 的向量检索优化 / DiskANN 实验”。  
> 当前建议：代码、数据集、索引都放在 WSL 的 Linux 文件系统中，例如 `~/projects`、`~/datasets`、`~/ann_exp`，不要放在 `/mnt/c`、`/mnt/d`。

---

## 0. 命令在哪里运行

| 命令类型 | 在哪里运行 | 例子 |
|---|---|---|
| Windows / WSL 管理命令 | PowerShell | `wsl -l -v` |
| Linux 命令 | WSL Ubuntu 终端 | `sudo apt update` |
| CMD 命令 | Windows CMD | `wmic logicaldisk get caption,freespace,size` |

判断当前是不是在 WSL 里：

```bash
whoami
pwd
uname -a
```

如果路径是：

```bash
/home/dzq
```

说明在 WSL 内部家目录，适合做实验。

如果路径是：

```bash
/mnt/c/Users/Dzq
```

说明当前在 Windows C 盘挂载目录，不建议在这里放 DiskANN 代码、数据集和索引。

---

## 1. Windows PowerShell：查看 WSL 状态

查看已安装的 WSL 发行版：

```powershell
wsl -l -v
```

示例：

```text
NAME              STATE           VERSION
* Ubuntu-24.04    Stopped         2
  docker-desktop  Stopped         2
```

含义：

- `Ubuntu-24.04`：你的 Ubuntu 发行版名称；
- `VERSION 2`：说明是 WSL2；
- `*`：默认启动的发行版；
- `Stopped`：当前没有运行，正常。

设置默认 WSL 发行版：

```powershell
wsl --set-default Ubuntu-24.04
```

进入指定 WSL：

```powershell
wsl -d Ubuntu-24.04
```

用 root 身份进入指定 WSL：

```powershell
wsl -d Ubuntu-24.04 -u root
```

关闭所有 WSL 实例：

```powershell
wsl --shutdown
```

查看 WSL 状态：

```powershell
wsl --status
```

---

## 2. Windows PowerShell：查看硬盘空间

查看各盘剩余空间：

```powershell
Get-PSDrive -PSProvider FileSystem
```

更清楚的 GB 版本：

```powershell
Get-PSDrive -PSProvider FileSystem |
Select Name,Root,@{n="FreeGB";e={[math]::Round($_.Free/1GB,1)}},@{n="UsedGB";e={[math]::Round($_.Used/1GB,1)}}
```

如果你在 CMD 里运行，会报：

```text
'Get-PSDrive' 不是内部或外部命令
```

原因是 `Get-PSDrive` 是 PowerShell 命令，不是 CMD 命令。

CMD 里可以用：

```cmd
wmic logicaldisk get caption,freespace,size
```

也可以在 CMD 里调用 PowerShell：

```cmd
powershell -NoProfile -Command "Get-PSDrive -PSProvider FileSystem | Select Name,Root,@{n='FreeGB';e={[math]::Round($_.Free/1GB,1)}},@{n='UsedGB';e={[math]::Round($_.Used/1GB,1)}}"
```

---

## 3. Windows PowerShell：查找 WSL 虚拟磁盘 ext4.vhdx

WSL2 的 Linux 文件系统通常存在一个虚拟磁盘文件：

```text
ext4.vhdx
```

在默认 Store 安装情况下，可以尝试：

```powershell
Get-ChildItem -Path $env:LOCALAPPDATA\Packages -Recurse -Filter ext4.vhdx -ErrorAction SilentlyContinue |
Select-Object FullName,@{Name="SizeGB";Expression={[math]::Round($_.Length/1GB,2)}}
```

如果搜不到，不一定代表 WSL 没有安装，可能是：

- Ubuntu 还很干净；
- 安装方式不是 Store 包路径；
- 已经通过 `wsl --import` 导入到了其他位置。

如果你已经迁移到了 D 盘，可以直接看：

```powershell
dir D:\WSL\Ubuntu-24.04
```

看到：

```text
ext4.vhdx
```

说明 WSL 虚拟磁盘在 D 盘对应目录中。

---

## 4. WSL 迁移到 D 盘：常用命令

### 4.1 创建目录

PowerShell：

```powershell
wsl --shutdown
mkdir D:\WSL
mkdir D:\WSL\backup
mkdir D:\WSL\Ubuntu-24.04
```

### 4.2 导出 Ubuntu

```powershell
wsl --export Ubuntu-24.04 D:\WSL\backup\Ubuntu-24.04.tar
```

导出时如果出现类似：

```text
无法配置网络 (networkingMode Mirrored)，回退到 networkingMode None。
操作成功完成。
```

只要最后有：

```text
操作成功完成。
```

通常说明导出成功。

### 4.3 确认 tar 备份存在

```powershell
dir D:\WSL\backup
```

或：

```powershell
Get-Item D:\WSL\backup\Ubuntu-24.04.tar
```

### 4.4 注销原来的 Ubuntu

非常重要：只有确认 `.tar` 文件存在后，才能执行这一步。

```powershell
wsl --unregister Ubuntu-24.04
```

注意：`wsl --unregister` 会删除原来的 WSL 发行版。

### 4.5 从 D 盘重新导入

```powershell
wsl --import Ubuntu-24.04 D:\WSL\Ubuntu-24.04 D:\WSL\backup\Ubuntu-24.04.tar --version 2
```

### 4.6 检查导入结果

```powershell
wsl -l -v
```

应该看到：

```text
Ubuntu-24.04      Stopped         2
```

### 4.7 设置默认发行版

```powershell
wsl --set-default Ubuntu-24.04
```

### 4.8 进入 WSL

```powershell
wsl -d Ubuntu-24.04
```

### 4.9 确认 D 盘里已有虚拟磁盘

```powershell
dir D:\WSL\Ubuntu-24.04
```

看到：

```text
ext4.vhdx
```

即可。

### 4.10 确认能正常进入后删除备份包

确认 WSL 能正常进入后，可删除备份 tar 节省空间：

```powershell
del D:\WSL\backup\Ubuntu-24.04.tar
```

---

## 5. WSL 网络配置常用命令

如果进入 WSL 时出现：

```text
无法配置网络 (networkingMode Mirrored)
检测到 localhost 代理配置，但未镜像到 WSL
```

可以在 PowerShell 中编辑 `.wslconfig`：

```powershell
notepad $env:USERPROFILE\.wslconfig
```

推荐内容：

```ini
[wsl2]
networkingMode=NAT
autoProxy=false
```

保存后：

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

进入 WSL 后测试网络：

```bash
ping -c 4 baidu.com
curl -I https://github.com
```

如果提示 `ping: command not found` 或 `curl: command not found`，先安装：

```bash
sudo apt update
sudo apt install -y iputils-ping curl ca-certificates
```

---

## 6. WSL 当前目录与实验目录

进入 WSL 后，如果在：

```bash
/mnt/c/Users/Dzq
```

先切回 Linux 家目录：

```bash
cd ~
pwd
```

希望看到：

```bash
/home/dzq
```

创建实验目录：

```bash
mkdir -p ~/projects ~/datasets ~/ann_exp
mkdir -p ~/ann_exp/{index,result,log,scripts}
```

目录建议：

| 目录 | 用途 |
|---|---|
| `~/projects` | 放 DiskANN 源码 |
| `~/datasets` | 放数据集 |
| `~/ann_exp` | 放实验脚本、索引、结果、日志 |
| `~/ann_exp/index` | 放构建出的索引 |
| `~/ann_exp/result` | 放实验结果 |
| `~/ann_exp/log` | 放环境信息、运行日志 |
| `~/ann_exp/scripts` | 放自己写的脚本 |

不要把正式实验放在：

```bash
/mnt/c/Users/Dzq
/mnt/d/...
```

原因：这些是 Windows 文件系统挂载目录，DiskANN 的 SSD IO 实验结果可能会变慢、不稳定、不干净。

---

## 7. WSL 用户与 sudo

查看当前用户：

```bash
whoami
```

查看用户组：

```bash
groups
```

如果用户不在 sudo 组，执行 `sudo apt update` 会报：

```text
dzq is not in the sudoers file.
```

修复方法：

PowerShell 用 root 进入：

```powershell
wsl -d Ubuntu-24.04 -u root
```

在 root 里执行：

```bash
usermod -aG sudo dzq
groups dzq
```

退出并重启：

```bash
exit
```

PowerShell：

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

再测试：

```bash
whoami
groups
sudo apt update
```

---

## 8. 创建普通用户

如果导入 WSL 后默认是 root，可以创建普通用户。

先安装必要工具：

```bash
apt update
apt install -y adduser sudo passwd
```

创建用户：

```bash
adduser dzq
usermod -aG sudo dzq
```

设置默认用户：

```bash
cat > /etc/wsl.conf <<EOF
[user]
default=dzq
EOF
```

退出并重启：

```bash
exit
```

PowerShell：

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

检查：

```bash
whoami
pwd
```

希望看到：

```text
dzq
/home/dzq
```

如果 `adduser` 不存在，可以先安装：

```bash
apt install -y adduser sudo passwd
```

或者用底层命令：

```bash
useradd -m -s /bin/bash dzq
passwd dzq
usermod -aG sudo dzq
```

---

## 9. Ubuntu 软件源与基础工具

更新软件源：

```bash
sudo apt update
```

升级系统包：

```bash
sudo apt upgrade -y
```

安装 ping、curl、证书：

```bash
sudo apt install -y iputils-ping curl ca-certificates
```

安装基础开发工具：

```bash
sudo apt install -y \
  build-essential \
  gcc \
  g++ \
  gdb \
  cmake \
  make \
  ninja-build \
  git \
  pkg-config \
  wget \
  unzip \
  zip \
  tar \
  python3 \
  python3-pip \
  python3-venv
```

安装 DiskANN 常用依赖和实验工具：

```bash
sudo apt install -y \
  libaio-dev \
  libboost-all-dev \
  libtbb-dev \
  libomp-dev \
  libopenblas-dev \
  liblapack-dev \
  libgoogle-perftools-dev \
  libssl-dev \
  zlib1g-dev \
  htop \
  iotop \
  sysstat \
  time \
  fio \
  numactl
```

可选：安装 clang-format 和 MKL：

```bash
sudo apt install -y clang-format libmkl-full-dev
```

如果安装 MKL 时出现：

```text
Use libmkl_rt.so as the default alternative to BLAS/LAPACK? [yes/no]
```

建议输入：

```text
no
```

因为你只是为了编译 DiskANN，不需要把 MKL 设置成整个系统默认 BLAS/LAPACK。

---

## 10. tzdata 时区选择

安装过程中如果出现：

```text
Configuring tzdata
Please select the geographic area in which you live.
```

中国大陆一般选择：

```text
5
```

代表 Asia。

后面城市选择：

```text
Shanghai
```

如果不想手动选，也可以之后执行：

```bash
sudo ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
sudo dpkg-reconfigure -f noninteractive tzdata
```

---

## 11. 检查编译器和工具版本

```bash
gcc --version
g++ --version
cmake --version
git --version
python3 --version
```

你当前曾经看到的版本类似：

```text
gcc/g++ 13.3.0
cmake 3.28.3
git 2.43.0
python 3.12.3
```

这些可以满足基础编译环境。

---

## 12. Python 虚拟环境

创建虚拟环境：

```bash
cd ~/ann_exp
python3 -m venv venv
```

激活：

```bash
source ~/ann_exp/venv/bin/activate
```

升级 pip：

```bash
pip install --upgrade pip
```

安装实验常用 Python 包：

```bash
pip install numpy pandas matplotlib scipy tqdm h5py
```

测试：

```bash
python - << 'PY'
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
print("Python env OK")
PY
```

退出虚拟环境：

```bash
deactivate
```

---

## 13. 记录实验环境

```bash
mkdir -p ~/ann_exp/log

{
  echo "===== OS ====="
  lsb_release -a
  echo
  echo "===== Kernel ====="
  uname -a
  echo
  echo "===== CPU ====="
  lscpu
  echo
  echo "===== Memory ====="
  free -h
  echo
  echo "===== Disk ====="
  df -h
  echo
  echo "===== Compiler ====="
  gcc --version
  g++ --version
  cmake --version
} > ~/ann_exp/log/environment.txt
```

查看：

```bash
cat ~/ann_exp/log/environment.txt
```

---

## 14. 磁盘与性能观察

查看 WSL Linux 文件系统空间：

```bash
df -h ~
```

查看内存：

```bash
free -h
```

查看 CPU 线程数：

```bash
nproc
```

查看 CPU 详情：

```bash
lscpu
```

查看磁盘 IO：

```bash
iostat -x 1 3
```

如果没有 `iostat`，安装：

```bash
sudo apt install -y sysstat
```

开启 sysstat：

```bash
sudo sed -i 's/ENABLED="false"/ENABLED="true"/' /etc/default/sysstat
sudo service sysstat restart || true
```

查看进程资源：

```bash
htop
```

查看 IO 进程：

```bash
sudo iotop
```

---

## 15. DiskANN 拉取与编译

进入项目目录：

```bash
cd ~/projects
```

拉取 DiskANN C++ 分支：

```bash
git clone --recursive -b cpp_main https://github.com/microsoft/DiskANN.git
```

进入源码目录：

```bash
cd ~/projects/DiskANN
```

创建构建目录：

```bash
mkdir -p build
cd build
```

CMake 配置：

```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
```

编译：

```bash
make -j$(nproc)
```

检查可执行程序：

```bash
ls ~/projects/DiskANN/build/apps
```

如果看到类似：

```text
build_memory_index
search_memory_index
build_disk_index
search_disk_index
```

说明编译成功。

如果 `git clone` 失败，可能是 GitHub 网络问题；如果 `cmake` 或 `make` 失败，保留最后 30 行报错方便排查：

```bash
make -j$(nproc) 2>&1 | tee ~/ann_exp/log/diskann_build.log
tail -n 30 ~/ann_exp/log/diskann_build.log
```

---

## 16. GitHub 网络测试

测试 GitHub：

```bash
curl -I https://github.com
```

如果 GitHub 不通，但 baidu 能通：

```bash
ping -c 4 baidu.com
```

说明 WSL 基础网络正常，只是 GitHub 访问不稳定。后续可以考虑：

- 重试；
- 使用代理；
- 使用镜像；
- 手动下载 zip 后复制到 WSL 内部目录。

---

## 17. 常见报错速查

### 报错：`Get-PSDrive 不是内部或外部命令`

原因：你在 CMD 里运行了 PowerShell 命令。  
解决：打开 PowerShell，或者在 CMD 里使用：

```cmd
powershell -NoProfile -Command "Get-PSDrive -PSProvider FileSystem"
```

### 报错：`adduser: command not found`

原因：Ubuntu 太精简，没有安装 `adduser`。  
解决：

```bash
apt update
apt install -y adduser sudo passwd
```

### 报错：`dzq is not in the sudoers file`

原因：用户没有加入 sudo 组。  
解决：

```powershell
wsl -d Ubuntu-24.04 -u root
```

然后：

```bash
usermod -aG sudo dzq
```

重启 WSL：

```powershell
wsl --shutdown
wsl -d Ubuntu-24.04
```

### 报错：`ping: command not found`

解决：

```bash
sudo apt install -y iputils-ping
```

### 报错：`curl: command not found`

解决：

```bash
sudo apt install -y curl ca-certificates
```

### WSL 一进入就在 `/mnt/c/Users/Dzq`

解决：

```bash
cd ~
pwd
```

只要后续项目放在 `/home/dzq` 下即可。

### 迁移时出现 `networkingMode Mirrored` 警告

只要最后显示：

```text
操作成功完成。
```

通常迁移或导入是成功的。后续可改 `.wslconfig`：

```powershell
notepad $env:USERPROFILE\.wslconfig
```

内容：

```ini
[wsl2]
networkingMode=NAT
autoProxy=false
```

然后：

```powershell
wsl --shutdown
```

---

## 18. 做 DiskANN 实验时的原则

1. 所有实验都在同一个环境下跑，保证相对对比公平。
2. 不要把代码、数据、索引放在 `/mnt/c`、`/mnt/d`。
3. 先小数据调通，再扩大规模。
4. 不要一开始碰 10M 数据集。
5. 建议路线：
   - 10K smoke test；
   - 100K 调试；
   - 500K 实验；
   - 空间和时间足够再尝试 SIFT1M。
6. 报告中要记录：
   - CPU；
   - 内存；
   - WSL2；
   - Ubuntu 版本；
   - 编译器版本；
   - 数据集规模；
   - 搜索参数；
   - QPS；
   - Recall；
   - Mean IOs；
   - 平均延迟；
   - 内存占用；
   - SSD / 文件系统输入输出。

---

## 3. Basic Task Full Command Playbook

> Source: `DiskANN_基础任务完整流程_命令版.md` (2,124 lines, 49 KB)

# DiskANN 选题二：基础任务完整流程与命令说明

> 适用对象：课程「计算机系统前沿」大作业，选题二「基于 SSD 的向量检索优化 / DiskANN 相关实验」  
> 适用环境：Windows + WSL2 + Ubuntu-24.04  
> 当前建议用户：`dzq`  
> 当前 DiskANN 目录：`~/projects/DiskANN`  
> 当前实验目录：`~/ann_exp/{data,index,result,log,scripts,figures}`  
> 当前推荐路线：先完整完成基础任务一、二、三，再做进阶三 cache 优化。

---

## 0. 阅读方式与重要约定

### 0.1 命令运行位置说明

本文档中每条命令都会标注运行位置：

- **Windows PowerShell**：在 Windows 的 PowerShell 里运行。
- **WSL 终端**：在 Ubuntu / VS Code Remote - WSL 终端里运行。

如果没有特别说明，DiskANN 实验相关命令都在 **WSL 终端**运行。

### 0.2 不要在 `/mnt/c` 或 `/mnt/d` 里跑实验

进入 WSL 后，路径如果是：

```bash
/mnt/c/Users/Dzq
```

说明你还在 Windows 文件系统挂载路径里。请先执行：

```bash
cd ~
pwd
```

你希望看到：

```text
/home/dzq
```

后续代码、数据、索引、日志都放在：

```text
~/projects
~/datasets
~/ann_exp
```

不要放在：

```text
/mnt/c/...
/mnt/d/...
```

原因：DiskANN 实验会涉及大量文件和随机 IO，放在 Windows 挂载目录会影响性能和实验可信度。

### 0.3 高风险命令说明

本文档尽量不使用删除命令。涉及删除、覆盖、重建索引时会明确提醒。  
`mkdir -p` 是安全命令：目录不存在就创建，存在就跳过，不会删除已有文件。

---

## 1. 三个基础任务整体理解

题目基础要求可以拆成三项：

```text
基础任务一：
阅读并理解 DiskANN 论文，下载 DiskANN 开源代码，配置环境并成功跑通。

基础任务二：
选择 1–2 个数据集，与内存版本 HNSW、NSG 或 Vamana 等算法进行性能对比。
报告中给出 QPS-Recall 曲线图，并保证公平性。

基础任务三：
对 DiskANN 算法进行 profile，例如 IO 次数、IO 时间占比、向量计算时间占比、
内存占用、SSD 占用等，分析 SSD 版算法与内存版算法的主要差异和性能瓶颈。
```

你当前推荐路线：

```text
对比对象：DiskANN 仓库自带 Memory Vamana
SSD 算法：DiskANN disk index
正式数据集：优先 SIFT1M
进阶方向：进阶三 cache 优化
```

这样做的好处是：

```text
不需要额外接 HNSW / NSG；
公平性更容易控制；
基础任务三可以自然引出 cache 优化；
工程风险比 RaBitQ 低。
```

---

## 2. 当前已经完成的部分

根据你当前终端输出，你已经完成：

```text
1. WSL2 Ubuntu-24.04 可用
2. WSL 用户：dzq
3. DiskANN 目录：/home/dzq/projects/DiskANN
4. DiskANN 分支：cpp_main
5. CMake 配置成功
6. make 编译成功
7. build/apps 下已经有：
   build_memory_index
   search_memory_index
   build_disk_index
   search_disk_index
8. ~/ann_exp 目录已经存在
```

你现在还需要继续完成：

```text
基础任务一：10K smoke test
基础任务二：SIFT1M Memory Vamana vs DiskANN SSD 对比
基础任务三：Profile 与瓶颈分析
```

---

# 第一部分：基础任务一完整流程

## 3. 基础任务一目标

基础任务一不是只要求编译成功，而是要证明：

```text
DiskANN 原版代码可以在你的机器上完整跑通。
```

推荐用小数据 smoke test 完成闭环：

```text
生成 10K base 数据
生成 1K query 数据
计算 groundtruth
构建 memory index
搜索 memory index
构建 disk index
搜索 disk index
计算 recall
保存日志
```

完成后你可以在报告里写：

```text
本文在 WSL2 Ubuntu-24.04 环境下配置并编译 DiskANN cpp_main 分支。
为验证环境正确性，使用随机生成的 10K base vectors 和 1K query vectors
完成 groundtruth 计算、内存索引构建与查询、磁盘索引构建与查询，
说明原版 DiskANN 流程可以在本机正常运行。
```

---

## 4. 确认仓库状态

### 4.1 确认路径、分支、工作区状态

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN
pwd
git branch --show-current
git status -sb
```

作用说明：

- `cd ~/projects/DiskANN`：进入 DiskANN 仓库。
- `pwd`：确认当前路径。
- `git branch --show-current`：查看当前分支，应该是 `cpp_main`。
- `git status -sb`：查看是否有未提交修改，最好是干净状态。

正常输出应包含：

```text
/home/dzq/projects/DiskANN
cpp_main
## cpp_main...origin/cpp_main
```

如果看到大量 `modified:`、`deleted:`，先不要自己处理，应该保存输出再分析。

---

## 5. 创建实验目录

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/{data,index,result,log,scripts,figures}
ls -la ~/ann_exp
```

作用说明：

- `data`：放数据文件，例如随机 10K 数据、SIFT1M 转换后的 `.bin`。
- `index`：放构建出的 memory index / disk index。
- `result`：放查询结果、CSV。
- `log`：放构建、搜索、profile 日志。
- `scripts`：放解析日志、切分数据、画图脚本。
- `figures`：放最终报告用图。

`mkdir -p` 不会删除已有内容，安全。

正常输出应包含：

```text
data
figures
index
log
result
scripts
```

---

## 6. 记录环境信息

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/log/environment_versions.txt <<'EOF'
===== OS =====
EOF

{
  echo "===== date ====="
  date

  echo
  echo "===== uname ====="
  uname -a

  echo
  echo "===== lsb_release ====="
  lsb_release -a 2>/dev/null || true

  echo
  echo "===== user ====="
  whoami
  pwd

  echo
  echo "===== cpu ====="
  nproc
  lscpu | head -n 30

  echo
  echo "===== memory ====="
  free -h

  echo
  echo "===== disk ====="
  df -h ~
  df -h ~/ann_exp

  echo
  echo "===== compiler ====="
  gcc --version | head -n 1
  g++ --version | head -n 1
  cmake --version | head -n 1
  make --version | head -n 1

  echo
  echo "===== DiskANN git ====="
  cd ~/projects/DiskANN
  git branch --show-current
  git rev-parse --short HEAD
  git status -sb
} | tee -a ~/ann_exp/log/environment_versions.txt
```

作用说明：

- 记录操作系统、CPU、内存、磁盘、编译器、DiskANN 分支和 commit。
- 这些内容后面可以写进报告“实验环境”部分。
- `tee -a` 表示一边显示，一边追加写入日志文件。

检查：

```bash
cat ~/ann_exp/log/environment_versions.txt | head -n 80
```

---

## 7. CMake 配置

你已经做过，后续如果需要复现，命令如下。

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release .. 2>&1 | tee ~/ann_exp/log/cmake_config.log
```

作用说明：

- `mkdir -p build`：创建编译目录。
- `cmake -DCMAKE_BUILD_TYPE=Release ..`：生成 Release 编译配置。
- `tee ~/ann_exp/log/cmake_config.log`：保存 CMake 日志。

正常输出结尾应包含：

```text
-- Configuring done
-- Generating done
-- Build files have been written to: /home/dzq/projects/DiskANN/build
```

如果失败，查看日志：

```bash
tail -n 80 ~/ann_exp/log/cmake_config.log
```

---

## 8. 编译 DiskANN

你已经编译成功，后续复现命令如下。

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build
make -j$(nproc) 2>&1 | tee ~/ann_exp/log/diskann_build.log
```

作用说明：

- `make`：正式编译。
- `-j$(nproc)`：使用当前 WSL 可用 CPU 线程数并行编译。
- `2>&1`：把错误输出也合并进日志。
- `tee`：保存编译日志。

如果担心笔记本发热，可以用慢一点的版本：

```bash
cd ~/projects/DiskANN/build
make -j4 2>&1 | tee ~/ann_exp/log/diskann_build.log
```

编译完成后检查：

```bash
ls ~/projects/DiskANN/build/apps
ls ~/projects/DiskANN/build/apps/utils
```

你应该能看到：

```text
build_memory_index
search_memory_index
build_disk_index
search_disk_index
```

以及工具：

```text
rand_data_gen
compute_groundtruth
calculate_recall
fvecs_to_bin
ivecs_to_bin
```

---

## 9. 检查核心程序帮助信息

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

./apps/utils/rand_data_gen --help | head -n 80
./apps/utils/compute_groundtruth --help | head -n 80
./apps/build_memory_index --help | head -n 80
./apps/build_disk_index --help | head -n 80
./apps/search_memory_index --help | head -n 80
./apps/search_disk_index --help | head -n 100
```

作用说明：

- 确认程序能启动。
- 查看当前分支的参数名，避免直接照搬其他版本命令。
- 如果出现 `error while loading shared libraries`，说明运行时库有问题，需要单独处理。

---

## 10. 生成 10K 随机数据

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

./apps/utils/rand_data_gen \
  --data_type float \
  --output_file ~/ann_exp/data/random10k_base.fbin \
  -D 128 \
  -N 10000 \
  --rand_scaling 10 \
  2>&1 | tee ~/ann_exp/log/gen_random10k_base.log
```

作用说明：

- 生成 10000 条 128 维 float base vectors。
- 输出文件：`~/ann_exp/data/random10k_base.fbin`。

继续生成 query：

```bash
./apps/utils/rand_data_gen \
  --data_type float \
  --output_file ~/ann_exp/data/random10k_query.fbin \
  -D 128 \
  -N 1000 \
  --rand_scaling 10 \
  2>&1 | tee ~/ann_exp/log/gen_random10k_query.log
```

作用说明：

- 生成 1000 条 128 维 float query vectors。
- 输出文件：`~/ann_exp/data/random10k_query.fbin`。

检查文件：

```bash
ls -lh ~/ann_exp/data/random10k_base.fbin ~/ann_exp/data/random10k_query.fbin
```

正常大小大约：

```text
random10k_base.fbin   4.9M
random10k_query.fbin  501K
```

---

## 11. 计算 10K groundtruth

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/utils/compute_groundtruth \
  --data_type float \
  --dist_fn l2 \
  --base_file ~/ann_exp/data/random10k_base.fbin \
  --query_file ~/ann_exp/data/random10k_query.fbin \
  --gt_file ~/ann_exp/data/random10k_gt \
  --K 10 \
  2>&1 | tee ~/ann_exp/log/gt_random10k.log
```

作用说明：

- `compute_groundtruth`：精确计算每个 query 的前 10 个最近邻。
- `--gt_file ~/ann_exp/data/random10k_gt`：建议不要手动加 `.bin` 后缀，后面搜索也使用同一个路径。
- `/usr/bin/time -v`：额外记录最大内存、文件系统输入输出等 profile 信息。
- 输出文件通常为：`~/ann_exp/data/random10k_gt`。

检查：

```bash
ls -lh ~/ann_exp/data/random10k_gt*
tail -n 30 ~/ann_exp/log/gt_random10k.log
```

正常日志应看到：

```text
Finished writing truthset
Exit status: 0
```

---

## 12. 构建 10K Memory Vamana 索引

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/index/memory

cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/build_memory_index \
  --data_type float \
  --dist_fn l2 \
  --data_path ~/ann_exp/data/random10k_base.fbin \
  --index_path_prefix ~/ann_exp/index/memory/random10k_R32_L50 \
  --max_degree 32 \
  --Lbuild 50 \
  --alpha 1.2 \
  --num_threads 4 \
  2>&1 | tee ~/ann_exp/log/build_memory_10k.log
```

作用说明：

- 构建内存版 Vamana 索引。
- `--max_degree 32`：图中每个点最多保留 32 条边。
- `--Lbuild 50`：构建时搜索候选集大小，越大索引质量越高但越慢。
- `--num_threads 4`：固定 4 线程，后面对比时保持公平。
- 输出索引前缀：`~/ann_exp/index/memory/random10k_R32_L50`。

检查：

```bash
ls -lh ~/ann_exp/index/memory | head
tail -n 40 ~/ann_exp/log/build_memory_10k.log
```

正常日志应看到：

```text
Index built
Exit status: 0
```

---

## 13. 搜索 10K Memory Vamana 索引

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/search_memory_index \
  --data_type float \
  --dist_fn l2 \
  --index_path_prefix ~/ann_exp/index/memory/random10k_R32_L50 \
  --query_file ~/ann_exp/data/random10k_query.fbin \
  --gt_file ~/ann_exp/data/random10k_gt \
  --recall_at 10 \
  --search_list 20 \
  --num_threads 4 \
  --result_path ~/ann_exp/result/memory_random10k_L20 \
  2>&1 | tee ~/ann_exp/log/search_memory_10k_L20.log
```

作用说明：

- `search_memory_index`：搜索内存版索引。
- `--search_list 20`：查询时候选集大小 L。
- `--gt_file`：用于计算 recall；如果日志显示找不到 truthset，可以后面用自定义脚本计算 recall。
- `--result_path`：结果文件前缀。

搜索后会生成类似文件：

```text
~/ann_exp/result/memory_random10k_L20_20_idx_uint32.bin
~/ann_exp/result/memory_random10k_L20_20_dists_float.bin
```

检查：

```bash
ls -lh ~/ann_exp/result | grep memory_random10k
tail -n 60 ~/ann_exp/log/search_memory_10k_L20.log
```

正常日志应看到：

```text
QPS
Mean Latency
99.9 Latency
Exit status: 0
```

---

## 14. 构建 10K DiskANN SSD 索引

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/index/disk

cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/build_disk_index \
  --data_type float \
  --dist_fn l2 \
  --data_path ~/ann_exp/data/random10k_base.fbin \
  --index_path_prefix ~/ann_exp/index/disk/random10k_R32_L50_B1_M1 \
  --search_DRAM_budget 0.2 \
  --build_DRAM_budget 1 \
  --max_degree 32 \
  --Lbuild 50 \
  --num_threads 4 \
  2>&1 | tee ~/ann_exp/log/build_disk_10k.log
```

作用说明：

- 构建 SSD 版 DiskANN 索引。
- `--search_DRAM_budget 0.2`：搜索阶段可用内存预算，单位通常为 GB。
- `--build_DRAM_budget 1`：构建阶段内存预算。
- `--max_degree 32`、`--Lbuild 50` 与内存版保持一致，便于公平比较。
- 输出索引前缀：`~/ann_exp/index/disk/random10k_R32_L50_B1_M1`。

检查：

```bash
ls -lh ~/ann_exp/index/disk | head
tail -n 60 ~/ann_exp/log/build_disk_10k.log
```

正常日志应看到：

```text
Finished writing
Indexing time
Exit status: 0
```

---

## 15. 搜索 10K DiskANN SSD 索引

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/search_disk_index \
  --data_type float \
  --dist_fn l2 \
  --index_path_prefix ~/ann_exp/index/disk/random10k_R32_L50_B1_M1 \
  --query_file ~/ann_exp/data/random10k_query.fbin \
  --gt_file ~/ann_exp/data/random10k_gt \
  --recall_at 10 \
  --search_list 20 \
  --beamwidth 2 \
  --num_nodes_to_cache 0 \
  --num_threads 4 \
  --result_path ~/ann_exp/result/disk_random10k_L20_W2_cache0 \
  2>&1 | tee ~/ann_exp/log/search_disk_10k_L20_W2_cache0.log
```

作用说明：

- `search_disk_index`：搜索 SSD 版 DiskANN 索引。
- `--beamwidth 2`：每轮并发读盘候选数，后续正式实验固定为 2。
- `--num_nodes_to_cache 0`：不启用 cache，作为 baseline。
- 输出结果前缀：`~/ann_exp/result/disk_random10k_L20_W2_cache0`。

搜索后会生成类似文件：

```text
~/ann_exp/result/disk_random10k_L20_W2_cache0_20_idx_uint32.bin
~/ann_exp/result/disk_random10k_L20_W2_cache0_20_dists_float.bin
```

检查：

```bash
ls -lh ~/ann_exp/result | grep disk_random10k
tail -n 80 ~/ann_exp/log/search_disk_10k_L20_W2_cache0.log
```

正常日志应看到：

```text
QPS
Mean Latency
Mean IOs
Mean IO (us)
Exit status: 0
```

---

## 16. 自定义计算 Recall 的脚本

如果 DiskANN 搜索日志没有直接打印 recall，或者提示：

```text
Truthset file ... not found. Not computing recall.
```

不要慌，可以用结果文件和 groundtruth 文件自己计算。

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/scripts/calc_recall.py <<'PY'
import argparse
import struct
import numpy as np
from pathlib import Path

def read_result_ids(path):
    path = Path(path)
    with path.open("rb") as f:
        n, d = struct.unpack("II", f.read(8))
        arr = np.fromfile(f, dtype=np.uint32, count=n * d)
    return arr.reshape(n, d)

def read_gt_ids(path):
    path = Path(path)
    with path.open("rb") as f:
        n, d = struct.unpack("II", f.read(8))
        ids = np.fromfile(f, dtype=np.uint32, count=n * d).reshape(n, d)
        # groundtruth 后半部分通常是 float distance，可以不读
    return ids

def recall_at_k(result_ids, gt_ids, k):
    result_ids = result_ids[:, :k]
    gt_ids = gt_ids[:, :k]
    total = result_ids.shape[0] * k
    hit = 0
    for res, gt in zip(result_ids, gt_ids):
        hit += len(set(res.tolist()) & set(gt.tolist()))
    return hit / total

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result_ids", required=True)
    ap.add_argument("--gt", required=True)
    ap.add_argument("--k", type=int, default=10)
    args = ap.parse_args()

    res = read_result_ids(args.result_ids)
    gt = read_gt_ids(args.gt)

    n = min(res.shape[0], gt.shape[0])
    res = res[:n]
    gt = gt[:n]

    r = recall_at_k(res, gt, args.k)
    print(f"n={n}, recall@{args.k}={r:.6f}")

if __name__ == "__main__":
    main()
PY
```

作用说明：

- 读取 DiskANN 搜索结果中的 `idx_uint32.bin` 文件。
- 读取 `compute_groundtruth` 生成的 truthset。
- 计算 Recall@K。

给脚本加执行权限：

```bash
chmod +x ~/ann_exp/scripts/calc_recall.py
```

计算 memory 10K recall：

```bash
python3 ~/ann_exp/scripts/calc_recall.py \
  --result_ids ~/ann_exp/result/memory_random10k_L20_20_idx_uint32.bin \
  --gt ~/ann_exp/data/random10k_gt \
  --k 10
```

计算 disk 10K recall：

```bash
python3 ~/ann_exp/scripts/calc_recall.py \
  --result_ids ~/ann_exp/result/disk_random10k_L20_W2_cache0_20_idx_uint32.bin \
  --gt ~/ann_exp/data/random10k_gt \
  --k 10
```

输出示例：

```text
n=1000, recall@10=0.xxxxxx
```

---

## 17. 基础任务一完成标准

完成以下文件后，基础任务一基本可以认为完成：

```text
~/ann_exp/log/environment_versions.txt
~/ann_exp/log/cmake_config.log
~/ann_exp/log/diskann_build.log
~/ann_exp/log/gen_random10k_base.log
~/ann_exp/log/gen_random10k_query.log
~/ann_exp/log/gt_random10k.log
~/ann_exp/log/build_memory_10k.log
~/ann_exp/log/search_memory_10k_L20.log
~/ann_exp/log/build_disk_10k.log
~/ann_exp/log/search_disk_10k_L20_W2_cache0.log
~/ann_exp/result/memory_random10k_L20_20_idx_uint32.bin
~/ann_exp/result/disk_random10k_L20_W2_cache0_20_idx_uint32.bin
```

最后检查命令：

```bash
ls -lh ~/ann_exp/log
ls -lh ~/ann_exp/result
```

---

# 第二部分：基础任务二完整流程

## 18. 基础任务二目标

基础任务二要求：

```text
选择 1–2 个数据集，与内存版本 HNSW、NSG 或 Vamana 等算法进行性能对比；
在报告中给出 QPS-Recall 曲线；
保证对比公平。
```

推荐选择：

```text
数据集：SIFT1M
内存版：Memory Vamana，也就是 build_memory_index / search_memory_index
SSD 版：DiskANN，也就是 build_disk_index / search_disk_index
```

公平性原则：

```text
同一数据集
同一 query
同一 groundtruth
同一 recall@10 指标
同一线程数，例如 4
构建参数尽量接近，例如 R=32, Lbuild=50
搜索参数只改变 L
```

不要出现：

```text
DiskANN 32 线程 vs Memory Vamana 1 线程
```

---

## 19. 准备 SIFT1M 数据集

### 19.1 下载数据集

运行位置：**WSL 终端**

```bash
mkdir -p ~/datasets
cd ~/datasets

wget -O sift.tar.gz ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz
```

作用说明：

- 下载 TexMex SIFT 数据集压缩包。
- 如果 `ftp://` 下载失败，可以用浏览器手动打开课程 PDF 给的数据集链接下载，然后把文件复制到 WSL 的 `~/datasets` 目录。

如果 `wget` 提示网络问题，可以先检查网络：

```bash
ping -c 4 baidu.com
curl -I https://github.com
```

解压：

```bash
cd ~/datasets
tar -xzf sift.tar.gz
ls -lh ~/datasets/sift
```

正常应能看到类似：

```text
sift_base.fvecs
sift_query.fvecs
sift_learn.fvecs
sift_groundtruth.ivecs
```

### 19.2 如果压缩包结构不同

运行位置：**WSL 终端**

```bash
find ~/datasets -maxdepth 3 -type f | grep -E "sift_.*\.(fvecs|ivecs)$"
```

作用说明：

- 找到 SIFT 文件实际路径。
- 如果文件不在 `~/datasets/sift`，后续命令中的路径要相应替换。

---

## 20. 转换 SIFT1M 为 DiskANN bin 格式

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/data/sift1m

cd ~/projects/DiskANN/build

./apps/utils/fvecs_to_bin float \
  ~/datasets/sift/sift_base.fvecs \
  ~/ann_exp/data/sift1m/sift_base.bin \
  2>&1 | tee ~/ann_exp/log/convert_sift_base.log
```

作用说明：

- 把 `sift_base.fvecs` 转成 DiskANN 使用的 `.bin` 格式。
- 输出：`~/ann_exp/data/sift1m/sift_base.bin`。

转换 query：

```bash
./apps/utils/fvecs_to_bin float \
  ~/datasets/sift/sift_query.fvecs \
  ~/ann_exp/data/sift1m/sift_query.bin \
  2>&1 | tee ~/ann_exp/log/convert_sift_query.log
```

作用说明：

- 把 `sift_query.fvecs` 转成 DiskANN 使用的 `.bin` 格式。
- 输出：`~/ann_exp/data/sift1m/sift_query.bin`。

检查：

```bash
ls -lh ~/ann_exp/data/sift1m
```

正常大小大约：

```text
sift_base.bin   489M
sift_query.bin  4.9M
```

---

## 21. 计算 SIFT1M groundtruth

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/utils/compute_groundtruth \
  --data_type float \
  --dist_fn l2 \
  --base_file ~/ann_exp/data/sift1m/sift_base.bin \
  --query_file ~/ann_exp/data/sift1m/sift_query.bin \
  --gt_file ~/ann_exp/data/sift1m/sift_gt \
  --K 10 \
  2>&1 | tee ~/ann_exp/log/sift1m_gt.log
```

作用说明：

- 精确计算 SIFT1M 的 groundtruth。
- `--K 10`：后续评估 Recall@10。
- 输出：`~/ann_exp/data/sift1m/sift_gt`。
- `/usr/bin/time -v` 会记录最大内存等信息。

检查：

```bash
ls -lh ~/ann_exp/data/sift1m/sift_gt*
tail -n 40 ~/ann_exp/log/sift1m_gt.log
```

正常应看到：

```text
Finished writing truthset
Exit status: 0
```

---

## 22. 可选：创建 1000 query 省时评估集

SIFT1M 全量 10000 query 在 WSL2 上搜索 SSD 版可能非常慢。建议先用 1000 query 做调试和初步对比。正式报告中可以说明：

```text
由于 WSL2 环境下 SSD 随机 IO 较慢，部分实验使用固定 1000 条 query 子集进行公平比较；
所有方法使用相同 query 子集和相同线程数。
```

### 22.1 创建切分脚本

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/scripts/slice_bin_float.py <<'PY'
import argparse
import struct
import numpy as np
from pathlib import Path

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
    data = np.fromfile(f, dtype=np.float32, count=n*d).reshape(n, d)

s = args.start
e = min(args.start + args.count, n)
sub = data[s:e].copy()

out.parent.mkdir(parents=True, exist_ok=True)
with out.open("wb") as f:
    f.write(struct.pack("II", sub.shape[0], sub.shape[1]))
    sub.astype(np.float32).tofile(f)

print(f"wrote {out}: n={sub.shape[0]}, d={sub.shape[1]}")
PY
```

作用说明：

- 读取 DiskANN `.bin` float 文件。
- 切出指定范围 query。
- 写成新的 `.bin` 文件。

### 22.2 切出 eval query

运行位置：**WSL 终端**

```bash
python3 ~/ann_exp/scripts/slice_bin_float.py \
  --input ~/ann_exp/data/sift1m/sift_query.bin \
  --output ~/ann_exp/data/sift1m/sift_query_eval_1000.bin \
  --start 0 \
  --count 1000
```

作用说明：

- 从 SIFT query 中取前 1000 条作为评估 query。
- 输出：`sift_query_eval_1000.bin`。

为 1000 query 单独计算 groundtruth：

```bash
cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/utils/compute_groundtruth \
  --data_type float \
  --dist_fn l2 \
  --base_file ~/ann_exp/data/sift1m/sift_base.bin \
  --query_file ~/ann_exp/data/sift1m/sift_query_eval_1000.bin \
  --gt_file ~/ann_exp/data/sift1m/sift_gt_eval_1000 \
  --K 10 \
  2>&1 | tee ~/ann_exp/log/sift1m_gt_eval_1000.log
```

作用说明：

- 为 1000 条评估 query 生成独立 groundtruth。
- 后面调试时用这个 groundtruth。

---

## 23. 构建 SIFT1M Memory Vamana 索引

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/index/memory

cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/build_memory_index \
  --data_type float \
  --dist_fn l2 \
  --data_path ~/ann_exp/data/sift1m/sift_base.bin \
  --index_path_prefix ~/ann_exp/index/memory/sift1m_R32_L50 \
  --max_degree 32 \
  --Lbuild 50 \
  --alpha 1.2 \
  --num_threads 4 \
  2>&1 | tee ~/ann_exp/log/build_memory_sift1m_R32_L50.log
```

作用说明：

- 构建 Memory Vamana 索引，作为内存版对比基线。
- `R=32`、`Lbuild=50` 是较轻量、适合个人电脑的参数。
- `--num_threads 4` 与 disk 版保持一致。

检查：

```bash
ls -lh ~/ann_exp/index/memory | grep sift1m
tail -n 60 ~/ann_exp/log/build_memory_sift1m_R32_L50.log
```

---

## 24. 构建 SIFT1M DiskANN SSD 索引

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/index/disk

cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/build_disk_index \
  --data_type float \
  --dist_fn l2 \
  --data_path ~/ann_exp/data/sift1m/sift_base.bin \
  --index_path_prefix ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4 \
  --search_DRAM_budget 1 \
  --build_DRAM_budget 4 \
  --max_degree 32 \
  --Lbuild 50 \
  --num_threads 4 \
  2>&1 | tee ~/ann_exp/log/build_disk_sift1m_R32_L50_B1_M4.log
```

作用说明：

- 构建 SSD 版 DiskANN 索引。
- `--search_DRAM_budget 1`：搜索阶段内存预算约 1GB。
- `--build_DRAM_budget 4`：构建阶段内存预算约 4GB。
- `R=32`、`Lbuild=50` 与 memory 版一致。
- 这个命令可能运行数分钟到几十分钟，视电脑性能而定。

检查：

```bash
ls -lh ~/ann_exp/index/disk | grep sift1m
tail -n 80 ~/ann_exp/log/build_disk_sift1m_R32_L50_B1_M4.log
```

---

## 25. 搜索 SIFT1M Memory Vamana：多个 L

运行位置：**WSL 终端**

使用全量 query 的版本：

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40 80 120; do
  echo "===== search memory L=${L} ====="
  /usr/bin/time -v ./apps/search_memory_index \
    --data_type float \
    --dist_fn l2 \
    --index_path_prefix ~/ann_exp/index/memory/sift1m_R32_L50 \
    --query_file ~/ann_exp/data/sift1m/sift_query.bin \
    --gt_file ~/ann_exp/data/sift1m/sift_gt \
    --recall_at 10 \
    --search_list ${L} \
    --num_threads 4 \
    --result_path ~/ann_exp/result/memory_sift1m_L${L} \
    2>&1 | tee ~/ann_exp/log/search_memory_sift1m_L${L}.log
done
```

作用说明：

- 固定线程数 4。
- 改变 `L = 10, 20, 40, 80, 120`。
- 得到 Memory Vamana 的 QPS-Recall 曲线数据。

省时 1000 query 版本：

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40 80 120; do
  echo "===== search memory eval1000 L=${L} ====="
  /usr/bin/time -v ./apps/search_memory_index \
    --data_type float \
    --dist_fn l2 \
    --index_path_prefix ~/ann_exp/index/memory/sift1m_R32_L50 \
    --query_file ~/ann_exp/data/sift1m/sift_query_eval_1000.bin \
    --gt_file ~/ann_exp/data/sift1m/sift_gt_eval_1000 \
    --recall_at 10 \
    --search_list ${L} \
    --num_threads 4 \
    --result_path ~/ann_exp/result/memory_sift1m_eval1000_L${L} \
    2>&1 | tee ~/ann_exp/log/search_memory_sift1m_eval1000_L${L}.log
done
```

---

## 26. 搜索 SIFT1M DiskANN SSD：多个 L

运行位置：**WSL 终端**

全量 query 版本：

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40 80 120; do
  echo "===== search disk L=${L} ====="
  /usr/bin/time -v ./apps/search_disk_index \
    --data_type float \
    --dist_fn l2 \
    --index_path_prefix ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4 \
    --query_file ~/ann_exp/data/sift1m/sift_query.bin \
    --gt_file ~/ann_exp/data/sift1m/sift_gt \
    --recall_at 10 \
    --search_list ${L} \
    --beamwidth 2 \
    --num_nodes_to_cache 0 \
    --num_threads 4 \
    --result_path ~/ann_exp/result/disk_sift1m_L${L}_W2_cache0 \
    2>&1 | tee ~/ann_exp/log/search_disk_sift1m_L${L}_W2_cache0.log
done
```

作用说明：

- 搜索 DiskANN SSD 索引。
- 固定 `beamwidth=2`。
- 固定 `cache_nodes=0`，作为 no-cache baseline。
- 固定线程数 4，保证和 memory 版公平。

省时 1000 query 版本：

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40 80 120; do
  echo "===== search disk eval1000 L=${L} ====="
  /usr/bin/time -v ./apps/search_disk_index \
    --data_type float \
    --dist_fn l2 \
    --index_path_prefix ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4 \
    --query_file ~/ann_exp/data/sift1m/sift_query_eval_1000.bin \
    --gt_file ~/ann_exp/data/sift1m/sift_gt_eval_1000 \
    --recall_at 10 \
    --search_list ${L} \
    --beamwidth 2 \
    --num_nodes_to_cache 0 \
    --num_threads 4 \
    --result_path ~/ann_exp/result/disk_sift1m_eval1000_L${L}_W2_cache0 \
    2>&1 | tee ~/ann_exp/log/search_disk_sift1m_eval1000_L${L}_W2_cache0.log
done
```

提醒：

```text
DiskANN SSD 搜索可能很慢。
如果 L=80 或 L=120 运行时间过长，可以先跑 L=10,20,40，
等确认流程无误后再补高 L。
```

---

## 27. 计算 SIFT1M Recall

如果搜索日志没有直接打印 recall，可以用第 16 节脚本。

全量 query memory recall：

```bash
for L in 10 20 40 80 120; do
  echo "memory L=${L}"
  python3 ~/ann_exp/scripts/calc_recall.py \
    --result_ids ~/ann_exp/result/memory_sift1m_L${L}_${L}_idx_uint32.bin \
    --gt ~/ann_exp/data/sift1m/sift_gt \
    --k 10
done
```

全量 query disk recall：

```bash
for L in 10 20 40 80 120; do
  echo "disk L=${L}"
  python3 ~/ann_exp/scripts/calc_recall.py \
    --result_ids ~/ann_exp/result/disk_sift1m_L${L}_W2_cache0_${L}_idx_uint32.bin \
    --gt ~/ann_exp/data/sift1m/sift_gt \
    --k 10
done
```

1000 query memory recall：

```bash
for L in 10 20 40 80 120; do
  echo "memory eval1000 L=${L}"
  python3 ~/ann_exp/scripts/calc_recall.py \
    --result_ids ~/ann_exp/result/memory_sift1m_eval1000_L${L}_${L}_idx_uint32.bin \
    --gt ~/ann_exp/data/sift1m/sift_gt_eval_1000 \
    --k 10
done
```

1000 query disk recall：

```bash
for L in 10 20 40 80 120; do
  echo "disk eval1000 L=${L}"
  python3 ~/ann_exp/scripts/calc_recall.py \
    --result_ids ~/ann_exp/result/disk_sift1m_eval1000_L${L}_W2_cache0_${L}_idx_uint32.bin \
    --gt ~/ann_exp/data/sift1m/sift_gt_eval_1000 \
    --k 10
done
```

---

## 28. 解析日志生成 baseline CSV

创建解析脚本。

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/scripts/parse_baseline_logs.py <<'PY'
import re
import csv
from pathlib import Path

LOG_DIR = Path.home() / "ann_exp" / "log"
OUT = Path.home() / "ann_exp" / "result" / "baseline_sift1m.csv"

def parse_timev(text):
    max_rss = None
    fs_inputs = None
    fs_outputs = None
    elapsed = None
    m = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    if m:
        max_rss = int(m.group(1)) / 1024.0
    m = re.search(r"File system inputs:\s*(\d+)", text)
    if m:
        fs_inputs = int(m.group(1))
    m = re.search(r"File system outputs:\s*(\d+)", text)
    if m:
        fs_outputs = int(m.group(1))
    m = re.search(r"Elapsed \(wall clock\) time.*:\s*([0-9:.]+)", text)
    if m:
        elapsed = m.group(1)
    return max_rss, fs_inputs, fs_outputs, elapsed

def parse_memory(text):
    # 匹配形如：
    # 40    12161.43            988.54              322.62        5212.72
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 5:
            try:
                L = int(parts[0])
                qps = float(parts[1])
                avg_cmps = float(parts[2])
                mean_latency = float(parts[3])
                p999 = float(parts[4])
                rows.append((L, qps, avg_cmps, mean_latency, p999))
            except ValueError:
                pass
    return rows[-1] if rows else None

def parse_disk(text):
    # 匹配形如：
    # 40 2 3.31 1208425.16 2089605.00 49.73 1206667.03 1432.81
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 8:
            try:
                L = int(parts[0])
                beam = int(parts[1])
                qps = float(parts[2])
                mean_latency = float(parts[3])
                p999 = float(parts[4])
                mean_ios = float(parts[5])
                mean_io_us = float(parts[6])
                cpu_s = float(parts[7])
                rows.append((L, beam, qps, mean_latency, p999, mean_ios, mean_io_us, cpu_s))
            except ValueError:
                pass
    return rows[-1] if rows else None

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    for path in sorted(LOG_DIR.glob("search_memory_sift1m*_L*.log")):
        text = path.read_text(errors="ignore")
        parsed = parse_memory(text)
        if not parsed:
            continue
        L, qps, avg_cmps, mean_latency, p999 = parsed
        max_rss, fs_inputs, fs_outputs, elapsed = parse_timev(text)
        dataset = "sift1m_eval1000" if "eval1000" in path.name else "sift1m"
        rows.append({
            "dataset": dataset,
            "method": "memory",
            "L": L,
            "beamwidth": 0,
            "cache_nodes": 0,
            "threads": 4,
            "qps": qps,
            "mean_latency_us": mean_latency,
            "p999_latency_us": p999,
            "mean_ios": "",
            "mean_io_us": "",
            "max_rss_mb": max_rss,
            "fs_inputs": fs_inputs,
            "fs_outputs": fs_outputs,
            "elapsed": elapsed,
            "log": path.name,
        })

    for path in sorted(LOG_DIR.glob("search_disk_sift1m*_L*_W2_cache0.log")):
        text = path.read_text(errors="ignore")
        parsed = parse_disk(text)
        if not parsed:
            continue
        L, beam, qps, mean_latency, p999, mean_ios, mean_io_us, cpu_s = parsed
        max_rss, fs_inputs, fs_outputs, elapsed = parse_timev(text)
        dataset = "sift1m_eval1000" if "eval1000" in path.name else "sift1m"
        rows.append({
            "dataset": dataset,
            "method": "disk",
            "L": L,
            "beamwidth": beam,
            "cache_nodes": 0,
            "threads": 4,
            "qps": qps,
            "mean_latency_us": mean_latency,
            "p999_latency_us": p999,
            "mean_ios": mean_ios,
            "mean_io_us": mean_io_us,
            "max_rss_mb": max_rss,
            "fs_inputs": fs_inputs,
            "fs_outputs": fs_outputs,
            "elapsed": elapsed,
            "log": path.name,
        })

    fieldnames = [
        "dataset","method","L","beamwidth","cache_nodes","threads",
        "qps","mean_latency_us","p999_latency_us","mean_ios","mean_io_us",
        "max_rss_mb","fs_inputs","fs_outputs","elapsed","log"
    ]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {OUT}, rows={len(rows)}")

if __name__ == "__main__":
    main()
PY
```

运行解析：

```bash
python3 ~/ann_exp/scripts/parse_baseline_logs.py
cat ~/ann_exp/result/baseline_sift1m.csv
```

作用说明：

- 从 `search_memory_*` 和 `search_disk_*` 日志中提取 QPS、延迟、Mean IOs、RSS、fs_inputs。
- 生成基础实验 CSV。

注意：

```text
这个脚本不自动填 recall。
Recall 可以用 calc_recall.py 计算后手动加到 CSV，或者后续再扩展脚本。
```

---

## 29. 手动创建包含 Recall 的 CSV 模板

如果不想一开始就自动化所有内容，可以先手动建立一个 CSV 模板。

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/result/baseline_sift1m_with_recall.csv <<'EOF'
dataset,method,L,beamwidth,cache_nodes,threads,recall@10,qps,mean_latency_us,p999_latency_us,mean_ios,mean_io_us,max_rss_mb,fs_inputs,fs_outputs
sift1m,memory,10,0,0,4,,,,,,,,
sift1m,memory,20,0,0,4,,,,,,,,
sift1m,memory,40,0,0,4,,,,,,,,
sift1m,memory,80,0,0,4,,,,,,,,
sift1m,memory,120,0,0,4,,,,,,,,
sift1m,disk,10,2,0,4,,,,,,,,
sift1m,disk,20,2,0,4,,,,,,,,
sift1m,disk,40,2,0,4,,,,,,,,
sift1m,disk,80,2,0,4,,,,,,,,
sift1m,disk,120,2,0,4,,,,,,,,
EOF
```

作用说明：

- 先建立报告需要的标准字段。
- 后面把日志解析结果和 recall 手动填进去也可以。

---

## 30. 画 QPS-Recall 曲线

创建画图脚本。

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/scripts/plot_qps_recall.py <<'PY'
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

df = pd.read_csv(args.csv)
df = df.dropna(subset=["recall@10", "qps"])

plt.figure()
for method, g in df.groupby("method"):
    g = g.sort_values("recall@10")
    plt.plot(g["recall@10"], g["qps"], marker="o", label=method)

plt.xlabel("Recall@10")
plt.ylabel("QPS")
plt.title("QPS-Recall Curve on SIFT1M")
plt.legend()
plt.grid(True)
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
plt.savefig(args.out, dpi=200, bbox_inches="tight")
print(f"saved {args.out}")
PY
```

作用说明：

- 输入含 `recall@10` 和 `qps` 的 CSV。
- 输出 QPS-Recall 曲线图。
- 图中文字使用英文，适合论文/报告图表。

运行：

```bash
python3 ~/ann_exp/scripts/plot_qps_recall.py \
  --csv ~/ann_exp/result/baseline_sift1m_with_recall.csv \
  --out ~/ann_exp/figures/qps_recall_sift1m.png
```

检查：

```bash
ls -lh ~/ann_exp/figures/qps_recall_sift1m.png
```

---

# 第三部分：基础任务三完整流程

## 31. 基础任务三目标

基础任务三要求你 profile DiskANN，并分析：

```text
SSD 版 DiskANN 与内存版 Vamana 的主要差异是什么？
SSD 版 DiskANN 的性能瓶颈是什么？
```

你要重点证明：

```text
DiskANN SSD 查询过程主要瓶颈来自 SSD 随机 IO，
而不是单纯的 CPU 向量计算。
```

---

## 32. Profile 指标来源

建议统计这些指标：

| 指标 | 来源 |
|---|---|
| QPS | search 日志 |
| Mean Latency | search 日志 |
| P999 Latency | search 日志 |
| Mean IOs | disk search 日志 |
| Mean IO us | disk search 日志 |
| Max RSS | `/usr/bin/time -v` |
| fs_inputs | `/usr/bin/time -v` |
| fs_outputs | `/usr/bin/time -v` |
| index size | `du -sh` / `find` |
| IO 时间占比 | `mean_io_us / mean_latency_us` |

---

## 33. 统计索引文件大小

运行位置：**WSL 终端**

```bash
{
  echo "name,path,size_bytes,size_human"
  for p in ~/ann_exp/index/memory/* ~/ann_exp/index/disk/*; do
    if [ -e "$p" ]; then
      bytes=$(stat -c%s "$p" 2>/dev/null || echo 0)
      human=$(du -h "$p" | awk '{print $1}')
      name=$(basename "$p")
      echo "$name,$p,$bytes,$human"
    fi
  done
} > ~/ann_exp/result/index_size_summary_sift1m.csv

cat ~/ann_exp/result/index_size_summary_sift1m.csv
```

作用说明：

- 统计 memory index 与 disk index 相关文件大小。
- 报告里用于说明 SSD 占用和内存版/磁盘版存储差异。

---

## 34. 生成 profile summary

如果第 28 节的解析脚本已经运行，会得到：

```text
~/ann_exp/result/baseline_sift1m.csv
```

可以复制一份作为 profile summary：

```bash
cp ~/ann_exp/result/baseline_sift1m.csv ~/ann_exp/result/profile_summary_sift1m.csv
```

作用说明：

- `profile_summary_sift1m.csv` 作为后续报告中 profile 表格的主数据。
- 如果你手动加入 recall 和 IO ratio，也可以另存为更完整版本。

创建 IO ratio 脚本：

```bash
cat > ~/ann_exp/scripts/add_io_ratio.py <<'PY'
import argparse
import pandas as pd
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True)
ap.add_argument("--output", required=True)
args = ap.parse_args()

df = pd.read_csv(args.input)

def calc(row):
    try:
        mean_io = float(row.get("mean_io_us", np.nan))
        mean_lat = float(row.get("mean_latency_us", np.nan))
        if mean_lat > 0:
            return mean_io / mean_lat
    except Exception:
        pass
    return np.nan

df["io_time_ratio"] = df.apply(calc, axis=1)
df.to_csv(args.output, index=False)
print(f"wrote {args.output}")
PY
```

运行：

```bash
python3 ~/ann_exp/scripts/add_io_ratio.py \
  --input ~/ann_exp/result/profile_summary_sift1m.csv \
  --output ~/ann_exp/result/profile_summary_sift1m_with_io_ratio.csv

cat ~/ann_exp/result/profile_summary_sift1m_with_io_ratio.csv
```

作用说明：

- 计算 `mean_io_us / mean_latency_us`。
- 这个比例可以用来说明 SSD 版 DiskANN 查询中 IO 等待占比高。

---

## 35. 画 Mean IOs vs L

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/scripts/plot_mean_ios.py <<'PY'
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

df = pd.read_csv(args.csv)
df = df[df["method"] == "disk"].copy()
df["mean_ios"] = pd.to_numeric(df["mean_ios"], errors="coerce")
df = df.dropna(subset=["mean_ios"]).sort_values("L")

plt.figure()
plt.plot(df["L"], df["mean_ios"], marker="o")
plt.xlabel("Search List L")
plt.ylabel("Mean IOs")
plt.title("Mean IOs vs Search List L")
plt.grid(True)
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
plt.savefig(args.out, dpi=200, bbox_inches="tight")
print(f"saved {args.out}")
PY
```

运行：

```bash
python3 ~/ann_exp/scripts/plot_mean_ios.py \
  --csv ~/ann_exp/result/profile_summary_sift1m.csv \
  --out ~/ann_exp/figures/mean_ios_vs_L.png
```

作用说明：

- 展示 L 增大时平均 IO 次数的变化。
- 这张图可以支撑“Recall 提升伴随更多随机 IO”的结论。

---

## 36. 画延迟 vs L

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/scripts/plot_latency_vs_L.py <<'PY'
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

df = pd.read_csv(args.csv)
df["mean_latency_us"] = pd.to_numeric(df["mean_latency_us"], errors="coerce")
df = df.dropna(subset=["mean_latency_us"])

plt.figure()
for method, g in df.groupby("method"):
    g = g.sort_values("L")
    plt.plot(g["L"], g["mean_latency_us"], marker="o", label=method)

plt.xlabel("Search List L")
plt.ylabel("Mean Latency (us)")
plt.title("Mean Latency vs Search List L")
plt.legend()
plt.grid(True)
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
plt.savefig(args.out, dpi=200, bbox_inches="tight")
print(f"saved {args.out}")
PY
```

运行：

```bash
python3 ~/ann_exp/scripts/plot_latency_vs_L.py \
  --csv ~/ann_exp/result/profile_summary_sift1m.csv \
  --out ~/ann_exp/figures/latency_vs_L.png
```

作用说明：

- 展示内存版和磁盘版延迟差异。
- 通常 DiskANN SSD 延迟显著高于 Memory Vamana。

---

## 37. 画 IO 时间占比

运行位置：**WSL 终端**

```bash
cat > ~/ann_exp/scripts/plot_io_ratio.py <<'PY'
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

df = pd.read_csv(args.csv)
df = df[df["method"] == "disk"].copy()
df["io_time_ratio"] = pd.to_numeric(df["io_time_ratio"], errors="coerce")
df = df.dropna(subset=["io_time_ratio"]).sort_values("L")

plt.figure()
plt.plot(df["L"], df["io_time_ratio"] * 100, marker="o")
plt.xlabel("Search List L")
plt.ylabel("IO Time Ratio (%)")
plt.title("IO Time Ratio vs Search List L")
plt.grid(True)
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
plt.savefig(args.out, dpi=200, bbox_inches="tight")
print(f"saved {args.out}")
PY
```

运行：

```bash
python3 ~/ann_exp/scripts/plot_io_ratio.py \
  --csv ~/ann_exp/result/profile_summary_sift1m_with_io_ratio.csv \
  --out ~/ann_exp/figures/io_time_ratio_vs_L.png
```

作用说明：

- 展示 IO 时间占平均查询延迟的比例。
- 如果比例很高，就能支撑“瓶颈是随机 IO 等待”的分析。

---

## 38. 基础任务三报告分析模板

报告中可以按这个逻辑写：

```text
为了分析 SSD 版 DiskANN 的性能瓶颈，本文在 SIFT1M 数据集上固定线程数为 4，
固定 beamwidth 为 2，改变搜索参数 L，并记录 QPS、平均延迟、P999 延迟、
Mean IOs、Mean IO 时间、最大内存占用和文件系统输入输出等指标。

实验结果显示，随着 L 增大，Recall@10 提升，但 QPS 下降、平均延迟上升。
相比 Memory Vamana，DiskANN SSD 查询过程中需要从 SSD 读取图节点和向量数据，
因此产生了大量随机 IO。Disk search 日志中的 Mean IOs 和 Mean IO(us) 随 L 增加而上升，
同时 /usr/bin/time -v 中的 file system inputs 也明显高于内存版搜索。

这说明 DiskANN SSD 的主要瓶颈不是单纯的 CPU 距离计算，而是 SSD 随机 IO 等待。
因此后续优化应围绕减少 IO 次数、提高 cache 命中率和改善访问局部性展开。
```

---

# 第四部分：建议的执行顺序

## 39. 你现在应该按这个顺序做

```text
第 1 步：完成 10K smoke test
  生成 random10k_base / random10k_query
  计算 random10k_gt
  build/search memory
  build/search disk
  计算 recall

第 2 步：准备 SIFT1M
  下载 / 解压
  fvecs_to_bin
  compute_groundtruth

第 3 步：构建正式索引
  build_memory_index
  build_disk_index

第 4 步：跑 baseline 对比
  Memory Vamana L=10/20/40/80/120
  DiskANN SSD L=10/20/40/80/120

第 5 步：整理结果
  calc_recall
  parse logs
  baseline_sift1m.csv
  qps_recall_sift1m.png

第 6 步：做 profile 分析
  profile_summary_sift1m.csv
  mean_ios_vs_L.png
  latency_vs_L.png
  io_time_ratio_vs_L.png

第 7 步：再开始进阶三 cache 优化
```

---

## 40. 最小必交产物清单

基础任务完成后，至少应有：

```text
日志：
~/ann_exp/log/environment_versions.txt
~/ann_exp/log/cmake_config.log
~/ann_exp/log/diskann_build.log
~/ann_exp/log/build_memory_10k.log
~/ann_exp/log/search_memory_10k_L20.log
~/ann_exp/log/build_disk_10k.log
~/ann_exp/log/search_disk_10k_L20_W2_cache0.log
~/ann_exp/log/build_memory_sift1m_R32_L50.log
~/ann_exp/log/build_disk_sift1m_R32_L50_B1_M4.log
~/ann_exp/log/search_memory_sift1m_L*.log
~/ann_exp/log/search_disk_sift1m_L*_W2_cache0.log

结果：
~/ann_exp/result/baseline_sift1m.csv
~/ann_exp/result/profile_summary_sift1m.csv
~/ann_exp/result/index_size_summary_sift1m.csv

图：
~/ann_exp/figures/qps_recall_sift1m.png
~/ann_exp/figures/mean_ios_vs_L.png
~/ann_exp/figures/latency_vs_L.png
~/ann_exp/figures/io_time_ratio_vs_L.png

脚本：
~/ann_exp/scripts/calc_recall.py
~/ann_exp/scripts/parse_baseline_logs.py
~/ann_exp/scripts/plot_qps_recall.py
~/ann_exp/scripts/plot_mean_ios.py
~/ann_exp/scripts/plot_latency_vs_L.py
~/ann_exp/scripts/plot_io_ratio.py
```

---

## 41. 常见问题判断

### 41.1 CMake 成功标志

```text
-- Configuring done
-- Generating done
-- Build files have been written to ...
```

### 41.2 make 成功标志

```text
[100%] Built target ...
```

并且：

```bash
ls ~/projects/DiskANN/build/apps
```

能看到：

```text
build_memory_index
search_memory_index
build_disk_index
search_disk_index
```

### 41.3 搜索成功标志

Memory search 日志中有：

```text
QPS
Mean Latency
99.9 Latency
Done searching. Now saving results
Exit status: 0
```

Disk search 日志中有：

```text
QPS
Mean Latency
Mean IOs
Mean IO (us)
Done searching. Now saving results
Exit status: 0
```

### 41.4 如果提示 groundtruth 找不到

例如：

```text
Truthset file xxx not found. Not computing recall.
```

处理方式：

```text
1. 先确认搜索结果文件已经生成；
2. 使用 ~/ann_exp/scripts/calc_recall.py 手动计算 recall；
3. 后续搜索命令中 --gt_file 尽量与 compute_groundtruth 的 --gt_file 完全一致。
```

---

## 42. 后续衔接进阶三 cache 优化

基础任务三得出瓶颈之后，可以自然引出进阶三：

```text
由于 DiskANN SSD 的主要瓶颈来自随机 IO，
本文进一步设计基于查询访问热点的 cache 策略。
通过训练 query 统计高频访问节点，将热点节点放入内存，
减少查询阶段 SSD 读取次数，从而降低平均延迟并提升 QPS。
```

建议进阶命名不要直接照搬朋友项目，可以使用：

```text
FHC：Frequency-based Hot Cache
```

或者：

```text
HHC：Hybrid Hot Cache
```

推荐实验设置：

```text
L = 40
beamwidth = 2
threads = 4
cache_nodes = 0, 5000, 10000, 20000
train query = 1000
eval query = 1000
策略 = none / bfs / hot / hybrid
```

但注意：在基础任务完成前，不要急着改源码。

---

## 43. 最后提醒

1. 每次贴终端输出时，优先贴最后 50–100 行日志。
2. 任何 `rm`、覆盖源码、重建 WSL、重装依赖的操作都先暂停确认。
3. 跑正式 SIFT1M 前，先跑完 10K smoke test。
4. 正式实验对比必须统一线程数。
5. DiskANN SSD 搜索很慢是正常现象，尤其在 WSL2 中。
6. 报告中不要夸大轻量实验，例如 1000 query 子集要如实说明。
7. 朋友项目只能参考实验组织和思路，不要直接复制代码和报告表述。

---

## 4. Task 2 (SIFT1M Baseline) Detailed Commands

> Source: `DiskANN_任务二完整实验流程_命令详解版.md` (1,147 lines, 29 KB)

# DiskANN 选题二：基础任务二完整实验流程与命令说明

> 任务二目标：在正式数据集上完成 **Memory Vamana vs DiskANN SSD** 的公平性能对比，并画出 **QPS–Recall 曲线**。  
> 当前建议数据集：SIFT1M  
> 当前建议对比：DiskANN 仓库自带 Memory Vamana vs DiskANN SSD  
> 当前环境：Windows + WSL2 Ubuntu-24.04  
> 当前用户：`dzq`  
> DiskANN 编译目录：`~/projects/DiskANN/build`  
> 实验目录：`~/ann_exp/{data,index,result,log,scripts,figures}`

---

## 0. 重要解释：为什么 WSL 显示 951G，但你的硬盘实际不到 100G？

你在 WSL 里看到：

```bash
df -h ~
```

输出类似：

```text
/dev/sdd  1007G  5.0G  951G  1% /
```

这并不表示你的电脑真实物理硬盘还剩 951GB。

WSL2 的 Ubuntu 文件系统通常存放在 Windows 里的一个动态虚拟磁盘文件中，例如：

```text
D:\WSL\Ubuntu-24.04\ext4.vhdx
```

`df -h` 看到的是 Linux 虚拟文件系统的逻辑容量，不等于 Windows 物理盘真实剩余空间。真实限制取决于 `ext4.vhdx` 所在 Windows 分区还剩多少空间。

所以后续判断空间时要同时看：

```text
1. Windows D/C/E 盘真实剩余空间；
2. WSL ext4.vhdx 当前大小；
3. WSL 内部 df -h 显示的 Linux 文件系统状态。
```

如果 Windows 所在盘只剩不到 100GB，不要做 10M 数据集；SIFT1M 仍然可以做，但要控制中间文件和实验规模。建议先用 eval1000，即 SIFT1M 的 1000 条 query 子集，完成任务二曲线。

---

## 1. Windows 真实磁盘空间检查

运行位置：**Windows PowerShell**

```powershell
Get-PSDrive -PSProvider FileSystem |
Select Name,Root,@{n="FreeGB";e={[math]::Round($_.Free/1GB,1)}},@{n="UsedGB";e={[math]::Round($_.Used/1GB,1)}}
```

作用：

- 查看 Windows 各盘真实剩余空间。
- 重点看 WSL 所在盘，例如你之前迁移到 `D:\WSL\Ubuntu-24.04`，就重点看 D 盘。

查看 WSL 虚拟磁盘真实大小：

```powershell
Get-Item D:\WSL\Ubuntu-24.04\ext4.vhdx |
Select FullName,@{n="SizeGB";e={[math]::Round($_.Length/1GB,2)}}
```

作用：

- 查看 `ext4.vhdx` 当前实际占用 Windows 磁盘多少 GB。
- 后续下载数据、构建索引会让这个文件变大。

判断建议：

```text
D 盘真实剩余 >= 30GB：可以比较稳地做 SIFT1M 基础实验。
D 盘真实剩余 15GB~30GB：可以做，但建议优先 eval1000，少保留重复文件。
D 盘真实剩余 < 15GB：先清理空间，不建议继续下载正式数据集。
```

---

## 2. 进入 WSL 并确认路径

运行位置：**Windows PowerShell**

```powershell
wsl -d Ubuntu-24.04
```

进入后运行位置：**WSL 终端**

```bash
cd ~
pwd
whoami
```

正常应看到：

```text
/home/dzq
dzq
```

如果刚进入时在 `/mnt/c/Users/Dzq`，一定先 `cd ~`。正式实验不要在 `/mnt/c` 或 `/mnt/d` 目录里跑。

---

## 3. 确认 DiskANN 程序和实验目录

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build
ls ~/projects/DiskANN/build/apps
ls ~/projects/DiskANN/build/apps/utils
```

作用：

- 确认任务一编译出的程序还在。
- 任务二会用到：
  - `build_memory_index`
  - `search_memory_index`
  - `build_disk_index`
  - `search_disk_index`
  - `fvecs_to_bin`
  - `compute_groundtruth`

创建并确认实验目录：

```bash
mkdir -p ~/ann_exp/{data,index,result,log,scripts,figures}
ls -la ~/ann_exp
```

作用：

- `data`：放转换后的 SIFT 数据；
- `index`：放 memory/disk 索引；
- `result`：放搜索结果和 CSV；
- `log`：放所有运行日志；
- `scripts`：放解析和画图脚本；
- `figures`：放曲线图。

---

## 4. 任务二完整流程概览

推荐你按这个顺序做：

```text
A. 检查 Windows 真实磁盘空间
B. 下载 SIFT1M
C. 解压并确认 sift_base.fvecs / sift_query.fvecs
D. 转换为 DiskANN bin 格式
E. 切出 eval1000 查询子集
F. 为 eval1000 计算 groundtruth
G. 构建 SIFT1M Memory Vamana 索引
H. 构建 SIFT1M DiskANN SSD 索引
I. 搜索 Memory Vamana，L=10/20/40/80/120
J. 搜索 DiskANN SSD，L=10/20/40/80/120
K. 解析日志生成 CSV
L. 画 QPS–Recall 曲线
M. 保存日志、结果、图表，写入报告
```

由于你的物理硬盘不到 100GB，建议：

```text
先做 eval1000；
不要碰 10M 数据；
确认 eval1000 跑通后，再考虑是否跑全量 10000 query。
```

---

## 5. 下载 SIFT1M

运行位置：**WSL 终端**

```bash
cd ~
mkdir -p ~/datasets
cd ~/datasets
pwd
```

作用：

- 创建原始数据集目录。
- 正常路径应为 `/home/dzq/datasets`。

检查 `wget`：

```bash
which wget
```

如果有输出 `/usr/bin/wget`，继续下载。  
如果没有输出，运行：

```bash
sudo apt update
sudo apt install -y wget
```

下载 SIFT：

```bash
cd ~/datasets

wget -O sift.tar.gz ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz   2>&1 | tee ~/ann_exp/log/download_sift.log
```

作用：

- 下载 SIFT 数据集压缩包到 `~/datasets/sift.tar.gz`。
- 日志保存到 `~/ann_exp/log/download_sift.log`。

检查：

```bash
ls -lh ~/datasets/sift.tar.gz
```

如果下载失败，查看：

```bash
tail -n 50 ~/ann_exp/log/download_sift.log
```

备用方案：如果浏览器手动下载到了 Windows 的下载目录，例如 `C:\Users\Dzq\Downloads\sift.tar.gz`，在 WSL 中复制：

```bash
cp /mnt/c/Users/Dzq/Downloads/sift.tar.gz ~/datasets/sift.tar.gz
ls -lh ~/datasets/sift.tar.gz
```

注意：复制到 WSL 后，后续都使用 `~/datasets/sift.tar.gz`，不要直接在 `/mnt/c` 上跑实验。

---

## 6. 解压并确认 SIFT 文件

运行位置：**WSL 终端**

```bash
cd ~/datasets
tar -xzf sift.tar.gz
```

作用：

- 解压 SIFT 数据集。

查找关键文件：

```bash
find ~/datasets -maxdepth 4 -type f | grep -E "sift_.*\.(fvecs|ivecs)$"
```

你希望看到类似：

```text
sift_base.fvecs
sift_query.fvecs
sift_learn.fvecs
sift_groundtruth.ivecs
```

如果路径不是 `~/datasets/sift/sift_base.fvecs`，后续命令里的路径要替换成你实际找到的路径。

---

## 7. 检查 fvecs_to_bin 用法

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build
./apps/utils/fvecs_to_bin --help 2>&1 | head -n 80
```

作用：

- 确认当前 DiskANN 分支里 `fvecs_to_bin` 的参数形式。
- 常见用法如下：

```bash
./apps/utils/fvecs_to_bin float input.fvecs output.bin
```

如果后续转换报参数错误，把 `--help` 输出和报错贴出来。

---

## 8. 转换 SIFT1M 为 DiskANN bin 格式

创建输出目录：

```bash
mkdir -p ~/ann_exp/data/sift1m
```

转换 base：

```bash
cd ~/projects/DiskANN/build

./apps/utils/fvecs_to_bin float   ~/datasets/sift/sift_base.fvecs   ~/ann_exp/data/sift1m/sift_base.bin   2>&1 | tee ~/ann_exp/log/convert_sift_base.log
```

作用：

- 把 `sift_base.fvecs` 转换为 DiskANN 使用的 `.bin` 文件。
- 输出：`~/ann_exp/data/sift1m/sift_base.bin`。

转换 query：

```bash
cd ~/projects/DiskANN/build

./apps/utils/fvecs_to_bin float   ~/datasets/sift/sift_query.fvecs   ~/ann_exp/data/sift1m/sift_query.bin   2>&1 | tee ~/ann_exp/log/convert_sift_query.log
```

作用：

- 把 `sift_query.fvecs` 转换为 `.bin`。
- 输出：`~/ann_exp/data/sift1m/sift_query.bin`。

检查：

```bash
ls -lh ~/ann_exp/data/sift1m
```

大致应看到：

```text
sift_base.bin   约 489M
sift_query.bin  约 4.9M
```

如果路径不对，用下面命令找真实文件：

```bash
find ~/datasets -name "sift_base.fvecs"
find ~/datasets -name "sift_query.fvecs"
```

---

## 9. 切出 eval1000 查询子集

为了节省时间，先使用 SIFT1M 的前 1000 条 query 做公平对比。

创建脚本：

```bash
cat > ~/ann_exp/scripts/slice_float_bin.py <<'PY'
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
PY
```

作用：

- 读取 DiskANN 的 float `.bin` 文件；
- 切出指定数量的向量；
- 写成新的 `.bin` 文件。

切出 1000 条 query：

```bash
python3 ~/ann_exp/scripts/slice_float_bin.py   --input ~/ann_exp/data/sift1m/sift_query.bin   --output ~/ann_exp/data/sift1m/sift_query_eval1000.bin   --start 0   --count 1000
```

检查：

```bash
ls -lh ~/ann_exp/data/sift1m/sift_query_eval1000.bin
```

---

## 10. 计算 eval1000 groundtruth

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/utils/compute_groundtruth   --data_type float   --dist_fn l2   --base_file ~/ann_exp/data/sift1m/sift_base.bin   --query_file ~/ann_exp/data/sift1m/sift_query_eval1000.bin   --gt_file ~/ann_exp/data/sift1m/sift_gt_eval1000   --K 10   2>&1 | tee ~/ann_exp/log/sift1m_gt_eval1000.log
```

作用：

- 为 1000 条 query 计算精确前 10 近邻；
- 后续所有 eval1000 搜索都用这个 groundtruth；
- `/usr/bin/time -v` 记录内存、IO 等信息。

检查：

```bash
ls -lh ~/ann_exp/data/sift1m/sift_gt_eval1000*
tail -n 40 ~/ann_exp/log/sift1m_gt_eval1000.log
```

正常应看到：

```text
Finished writing truthset
Exit status: 0
```

---

## 11. 可选：计算全量 query groundtruth

如果 eval1000 全流程跑通，而且时间充足，再计算全量：

```bash
cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/utils/compute_groundtruth   --data_type float   --dist_fn l2   --base_file ~/ann_exp/data/sift1m/sift_base.bin   --query_file ~/ann_exp/data/sift1m/sift_query.bin   --gt_file ~/ann_exp/data/sift1m/sift_gt_full   --K 10   2>&1 | tee ~/ann_exp/log/sift1m_gt_full.log
```

如果时间或空间紧张，可以暂时不做全量，报告中诚实说明使用固定的 eval1000 query 子集。

---

## 12. 构建 Memory Vamana 索引

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/index/memory

cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/build_memory_index   --data_type float   --dist_fn l2   --data_path ~/ann_exp/data/sift1m/sift_base.bin   --index_path_prefix ~/ann_exp/index/memory/sift1m_R32_L50   --max_degree 32   --Lbuild 50   --alpha 1.2   --num_threads 4   2>&1 | tee ~/ann_exp/log/build_memory_sift1m_R32_L50.log
```

作用：

- 构建内存版 Vamana 索引；
- 这是任务二的内存版对比基线；
- `--max_degree 32`：图最大度；
- `--Lbuild 50`：构建时搜索候选集大小；
- `--alpha 1.2`：图剪枝参数；
- `--num_threads 4`：固定线程数，保证公平。

检查：

```bash
ls -lh ~/ann_exp/index/memory | grep sift1m
tail -n 60 ~/ann_exp/log/build_memory_sift1m_R32_L50.log
```

正常应看到：

```text
Index built
Exit status: 0
```

---

## 13. 构建 DiskANN SSD 索引

运行位置：**WSL 终端**

```bash
mkdir -p ~/ann_exp/index/disk

cd ~/projects/DiskANN/build

/usr/bin/time -v ./apps/build_disk_index   --data_type float   --dist_fn l2   --data_path ~/ann_exp/data/sift1m/sift_base.bin   --index_path_prefix ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4   --search_DRAM_budget 1   --build_DRAM_budget 4   --max_degree 32   --Lbuild 50   --num_threads 4   2>&1 | tee ~/ann_exp/log/build_disk_sift1m_R32_L50_B1_M4.log
```

作用：

- 构建 SSD 版 DiskANN 索引；
- `--search_DRAM_budget 1`：搜索阶段内存预算约 1GB；
- `--build_DRAM_budget 4`：构建阶段内存预算约 4GB；
- `R=32, Lbuild=50, threads=4` 与 memory 索引保持一致，保证公平；
- 这一步可能耗时较久，正常。

检查：

```bash
ls -lh ~/ann_exp/index/disk | grep sift1m
tail -n 100 ~/ann_exp/log/build_disk_sift1m_R32_L50_B1_M4.log
```

正常应看到：

```text
Output disk index file written to ...
Indexing time:
Exit status: 0
```

---

## 14. 搜索 Memory Vamana：eval1000，多组 L

运行位置：**WSL 终端**

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40 80 120; do
  echo "===== search memory eval1000 L=${L} ====="
  /usr/bin/time -v ./apps/search_memory_index     --data_type float     --dist_fn l2     --index_path_prefix ~/ann_exp/index/memory/sift1m_R32_L50     --query_file ~/ann_exp/data/sift1m/sift_query_eval1000.bin     --gt_file ~/ann_exp/data/sift1m/sift_gt_eval1000     --recall_at 10     --search_list ${L}     --num_threads 4     --result_path ~/ann_exp/result/memory_sift1m_eval1000_L${L}     2>&1 | tee ~/ann_exp/log/search_memory_sift1m_eval1000_L${L}.log
done
```

作用：

- 使用同一组 1000 query 搜索 memory index；
- 固定线程数 4；
- 改变 `L=10,20,40,80,120`；
- 得到 Memory Vamana 的 QPS–Recall 数据。

检查：

```bash
ls -lh ~/ann_exp/result | grep memory_sift1m_eval1000
tail -n 60 ~/ann_exp/log/search_memory_sift1m_eval1000_L40.log
```

正常日志中应有：

```text
QPS
Mean Latency
Recall@10
Exit status: 0
```

---

## 15. 搜索 DiskANN SSD：eval1000，多组 L

运行位置：**WSL 终端**

建议先跑 `10,20,40`，确认没问题后再补 `80,120`。

先跑前三组：

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40; do
  echo "===== search disk eval1000 L=${L} ====="
  /usr/bin/time -v ./apps/search_disk_index     --data_type float     --dist_fn l2     --index_path_prefix ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4     --query_file ~/ann_exp/data/sift1m/sift_query_eval1000.bin     --gt_file ~/ann_exp/data/sift1m/sift_gt_eval1000     --recall_at 10     --search_list ${L}     --beamwidth 2     --num_nodes_to_cache 0     --num_threads 4     --result_path ~/ann_exp/result/disk_sift1m_eval1000_L${L}_W2_cache0     2>&1 | tee ~/ann_exp/log/search_disk_sift1m_eval1000_L${L}_W2_cache0.log
done
```

确认成功后，再补：

```bash
cd ~/projects/DiskANN/build

for L in 80 120; do
  echo "===== search disk eval1000 L=${L} ====="
  /usr/bin/time -v ./apps/search_disk_index     --data_type float     --dist_fn l2     --index_path_prefix ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4     --query_file ~/ann_exp/data/sift1m/sift_query_eval1000.bin     --gt_file ~/ann_exp/data/sift1m/sift_gt_eval1000     --recall_at 10     --search_list ${L}     --beamwidth 2     --num_nodes_to_cache 0     --num_threads 4     --result_path ~/ann_exp/result/disk_sift1m_eval1000_L${L}_W2_cache0     2>&1 | tee ~/ann_exp/log/search_disk_sift1m_eval1000_L${L}_W2_cache0.log
done
```

作用：

- 搜索 DiskANN SSD 索引；
- 固定 `beamwidth=2`；
- 固定 `num_nodes_to_cache=0`，表示 no-cache baseline；
- 固定 `num_threads=4`，保证和 memory 版公平；
- 改变 L 形成 QPS–Recall 曲线。

检查：

```bash
tail -n 80 ~/ann_exp/log/search_disk_sift1m_eval1000_L40_W2_cache0.log
```

正常日志中应有：

```text
QPS
Mean Latency
Mean IOs
Mean IO (us)
Recall@10
Exit status: 0
```

---

## 16. 可选：全量 query 搜索

如果 eval1000 成功，且时间充足，可以跑全量 query。

Memory 全量：

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40 80 120; do
  echo "===== search memory full L=${L} ====="
  /usr/bin/time -v ./apps/search_memory_index     --data_type float     --dist_fn l2     --index_path_prefix ~/ann_exp/index/memory/sift1m_R32_L50     --query_file ~/ann_exp/data/sift1m/sift_query.bin     --gt_file ~/ann_exp/data/sift1m/sift_gt_full     --recall_at 10     --search_list ${L}     --num_threads 4     --result_path ~/ann_exp/result/memory_sift1m_full_L${L}     2>&1 | tee ~/ann_exp/log/search_memory_sift1m_full_L${L}.log
done
```

Disk 全量：

```bash
cd ~/projects/DiskANN/build

for L in 10 20 40 80 120; do
  echo "===== search disk full L=${L} ====="
  /usr/bin/time -v ./apps/search_disk_index     --data_type float     --dist_fn l2     --index_path_prefix ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4     --query_file ~/ann_exp/data/sift1m/sift_query.bin     --gt_file ~/ann_exp/data/sift1m/sift_gt_full     --recall_at 10     --search_list ${L}     --beamwidth 2     --num_nodes_to_cache 0     --num_threads 4     --result_path ~/ann_exp/result/disk_sift1m_full_L${L}_W2_cache0     2>&1 | tee ~/ann_exp/log/search_disk_sift1m_full_L${L}_W2_cache0.log
done
```

如果只做 eval1000，报告中要写明：

```text
由于实验环境为个人电脑 WSL2，为控制实验时间和磁盘压力，本文使用固定的前 1000 条 query 作为评估子集。所有方法使用相同 query 子集和同一 groundtruth，因此相对比较仍然公平。
```

---

## 17. 解析日志生成 CSV

创建解析脚本：

```bash
cat > ~/ann_exp/scripts/parse_task2_logs.py <<'PY'
import re
import csv
from pathlib import Path

LOG_DIR = Path.home() / "ann_exp" / "log"
OUT = Path.home() / "ann_exp" / "result" / "task2_baseline_eval1000.csv"

def parse_timev(text):
    rss = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", text)
    fin = re.search(r"File system inputs:\s*(\d+)", text)
    fout = re.search(r"File system outputs:\s*(\d+)", text)
    elapsed = re.search(r"Elapsed \(wall clock\) time.*:\s*([0-9:.]+)", text)
    return {
        "max_rss_mb": round(int(rss.group(1)) / 1024, 2) if rss else "",
        "fs_inputs": int(fin.group(1)) if fin else "",
        "fs_outputs": int(fout.group(1)) if fout else "",
        "elapsed": elapsed.group(1) if elapsed else "",
    }

def parse_memory(text):
    # L QPS AvgDistCmps MeanLatency P999 Recall
    rows = []
    for line in text.splitlines():
        p = line.split()
        if len(p) == 6:
            try:
                rows.append({
                    "L": int(p[0]),
                    "qps": float(p[1]),
                    "avg_dist_cmps": float(p[2]),
                    "mean_latency_us": float(p[3]),
                    "p999_latency_us": float(p[4]),
                    "recall@10": float(p[5]),
                })
            except ValueError:
                pass
    return rows[-1] if rows else None

def parse_disk(text):
    # L Beamwidth QPS MeanLatency P999 MeanIOs MeanIOus CPU Recall
    rows = []
    for line in text.splitlines():
        p = line.split()
        if len(p) == 9:
            try:
                rows.append({
                    "L": int(p[0]),
                    "beamwidth": int(p[1]),
                    "qps": float(p[2]),
                    "mean_latency_us": float(p[3]),
                    "p999_latency_us": float(p[4]),
                    "mean_ios": float(p[5]),
                    "mean_io_us": float(p[6]),
                    "cpu_s": float(p[7]),
                    "recall@10": float(p[8]),
                })
            except ValueError:
                pass
    return rows[-1] if rows else None

def main():
    rows = []

    for path in sorted(LOG_DIR.glob("search_memory_sift1m_eval1000_L*.log")):
        text = path.read_text(errors="ignore")
        m = parse_memory(text)
        if not m:
            continue
        t = parse_timev(text)
        rows.append({
            "dataset": "sift1m_eval1000",
            "method": "memory",
            "L": m["L"],
            "beamwidth": 0,
            "cache_nodes": 0,
            "threads": 4,
            "recall@10": m["recall@10"],
            "qps": m["qps"],
            "mean_latency_us": m["mean_latency_us"],
            "p999_latency_us": m["p999_latency_us"],
            "avg_dist_cmps": m["avg_dist_cmps"],
            "mean_ios": "",
            "mean_io_us": "",
            "io_time_ratio": "",
            "max_rss_mb": t["max_rss_mb"],
            "fs_inputs": t["fs_inputs"],
            "fs_outputs": t["fs_outputs"],
            "elapsed": t["elapsed"],
            "log": path.name,
        })

    for path in sorted(LOG_DIR.glob("search_disk_sift1m_eval1000_L*_W2_cache0.log")):
        text = path.read_text(errors="ignore")
        d = parse_disk(text)
        if not d:
            continue
        t = parse_timev(text)
        ratio = d["mean_io_us"] / d["mean_latency_us"] if d["mean_latency_us"] else ""
        rows.append({
            "dataset": "sift1m_eval1000",
            "method": "disk",
            "L": d["L"],
            "beamwidth": d["beamwidth"],
            "cache_nodes": 0,
            "threads": 4,
            "recall@10": d["recall@10"],
            "qps": d["qps"],
            "mean_latency_us": d["mean_latency_us"],
            "p999_latency_us": d["p999_latency_us"],
            "avg_dist_cmps": "",
            "mean_ios": d["mean_ios"],
            "mean_io_us": d["mean_io_us"],
            "io_time_ratio": ratio,
            "max_rss_mb": t["max_rss_mb"],
            "fs_inputs": t["fs_inputs"],
            "fs_outputs": t["fs_outputs"],
            "elapsed": t["elapsed"],
            "log": path.name,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "dataset","method","L","beamwidth","cache_nodes","threads",
        "recall@10","qps","mean_latency_us","p999_latency_us",
        "avg_dist_cmps","mean_ios","mean_io_us","io_time_ratio",
        "max_rss_mb","fs_inputs","fs_outputs","elapsed","log"
    ]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {OUT}, rows={len(rows)}")
    for r in rows:
        print(r)

if __name__ == "__main__":
    main()
PY
```

运行解析：

```bash
python3 ~/ann_exp/scripts/parse_task2_logs.py
cat ~/ann_exp/result/task2_baseline_eval1000.csv
```

作用：

- 从 memory/disk 搜索日志中提取：
  - Recall@10
  - QPS
  - Mean Latency
  - P999
  - Mean IOs
  - Mean IO(us)
  - Max RSS
  - File system inputs/outputs
- 生成任务二结果 CSV。

---

## 18. 画 QPS–Recall 曲线

创建画图脚本：

```bash
cat > ~/ann_exp/scripts/plot_task2_qps_recall.py <<'PY'
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
PY
```

运行：

```bash
python3 ~/ann_exp/scripts/plot_task2_qps_recall.py   --csv ~/ann_exp/result/task2_baseline_eval1000.csv   --out ~/ann_exp/figures/task2_qps_recall_eval1000.png
```

检查：

```bash
ls -lh ~/ann_exp/figures/task2_qps_recall_eval1000.png
```

---

## 19. 画 L–Recall 和 L–QPS 曲线

创建 L–Recall 脚本：

```bash
cat > ~/ann_exp/scripts/plot_task2_L_recall.py <<'PY'
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

df = pd.read_csv(args.csv)
df["L"] = pd.to_numeric(df["L"], errors="coerce")
df["recall@10"] = pd.to_numeric(df["recall@10"], errors="coerce")
df = df.dropna(subset=["L", "recall@10"])

plt.figure()
for method, g in df.groupby("method"):
    g = g.sort_values("L")
    plt.plot(g["L"], g["recall@10"], marker="o", label=method)

plt.xlabel("Search List L")
plt.ylabel("Recall@10")
plt.title("Recall@10 vs Search List L")
plt.legend()
plt.grid(True)

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, dpi=200, bbox_inches="tight")
print(f"saved {out}")
PY
```

运行：

```bash
python3 ~/ann_exp/scripts/plot_task2_L_recall.py   --csv ~/ann_exp/result/task2_baseline_eval1000.csv   --out ~/ann_exp/figures/task2_L_recall_eval1000.png
```

创建 L–QPS 脚本：

```bash
cat > ~/ann_exp/scripts/plot_task2_L_qps.py <<'PY'
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--csv", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()

df = pd.read_csv(args.csv)
df["L"] = pd.to_numeric(df["L"], errors="coerce")
df["qps"] = pd.to_numeric(df["qps"], errors="coerce")
df = df.dropna(subset=["L", "qps"])

plt.figure()
for method, g in df.groupby("method"):
    g = g.sort_values("L")
    plt.plot(g["L"], g["qps"], marker="o", label=method)

plt.xlabel("Search List L")
plt.ylabel("QPS")
plt.title("QPS vs Search List L")
plt.legend()
plt.grid(True)

out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, dpi=200, bbox_inches="tight")
print(f"saved {out}")
PY
```

运行：

```bash
python3 ~/ann_exp/scripts/plot_task2_L_qps.py   --csv ~/ann_exp/result/task2_baseline_eval1000.csv   --out ~/ann_exp/figures/task2_L_qps_eval1000.png
```

---

## 20. 统计索引文件大小

运行位置：**WSL 终端**

```bash
{
  echo "method,file,size_bytes,size_human"
  for f in ~/ann_exp/index/memory/sift1m_R32_L50*; do
    if [ -e "$f" ]; then
      echo "memory,$f,$(stat -c%s "$f"),$(du -h "$f" | awk '{print $1}')"
    fi
  done
  for f in ~/ann_exp/index/disk/sift1m_R32_L50_B1_M4*; do
    if [ -e "$f" ]; then
      echo "disk,$f,$(stat -c%s "$f"),$(du -h "$f" | awk '{print $1}')"
    fi
  done
} > ~/ann_exp/result/task2_index_size_summary.csv

cat ~/ann_exp/result/task2_index_size_summary.csv
```

作用：

- 统计 memory index 和 disk index 的文件大小。
- 这些数据可用于任务二报告，也会在任务三 profile 中继续使用。

---

## 21. 任务二完成标准

eval1000 版本至少应产生：

```text
数据：
~/ann_exp/data/sift1m/sift_base.bin
~/ann_exp/data/sift1m/sift_query.bin
~/ann_exp/data/sift1m/sift_query_eval1000.bin
~/ann_exp/data/sift1m/sift_gt_eval1000

索引：
~/ann_exp/index/memory/sift1m_R32_L50*
~/ann_exp/index/disk/sift1m_R32_L50_B1_M4*

日志：
~/ann_exp/log/build_memory_sift1m_R32_L50.log
~/ann_exp/log/build_disk_sift1m_R32_L50_B1_M4.log
~/ann_exp/log/search_memory_sift1m_eval1000_L*.log
~/ann_exp/log/search_disk_sift1m_eval1000_L*_W2_cache0.log

结果：
~/ann_exp/result/task2_baseline_eval1000.csv
~/ann_exp/result/task2_index_size_summary.csv

图：
~/ann_exp/figures/task2_qps_recall_eval1000.png
~/ann_exp/figures/task2_L_recall_eval1000.png
~/ann_exp/figures/task2_L_qps_eval1000.png
```

最终检查：

```bash
ls -lh ~/ann_exp/result
ls -lh ~/ann_exp/figures
```

---

## 22. 报告中任务二可写内容

可以这样写：

```text
本文选择 SIFT1M 作为正式实验数据集。由于实验环境为个人电脑 WSL2，
为控制运行时间，本文使用固定的前 1000 条 query 作为评估子集。
所有方法均使用相同 base 数据、相同 query 子集和相同 groundtruth，
因此相对比较仍然公平。

对比方法包括：
1. Memory Vamana：DiskANN 仓库提供的内存版图索引；
2. DiskANN SSD：基于 SSD 的磁盘索引。

为了保证公平性，两种方法均使用 4 个线程，构建参数保持一致：
max_degree=32，Lbuild=50。搜索阶段改变 search list L，
取 L = 10, 20, 40, 80, 120。DiskANN SSD 额外固定 beamwidth=2，
并设置 num_nodes_to_cache=0 作为 no-cache baseline。

实验结果表明，随着 L 增大，Recall@10 提升，但 QPS 下降。
Memory Vamana 的 QPS 明显高于 DiskANN SSD，因为其主要访问内存中的图和向量；
DiskANN SSD 则需要读取磁盘节点，因此查询延迟更高。
```

---

## 23. 空间控制建议

查看 WSL 内部目录占用：

```bash
du -sh ~/datasets ~/ann_exp ~/projects 2>/dev/null
```

查看 Windows 真实剩余空间：

```powershell
Get-PSDrive -PSProvider FileSystem |
Select Name,Root,@{n="FreeGB";e={[math]::Round($_.Free/1GB,1)}},@{n="UsedGB";e={[math]::Round($_.Used/1GB,1)}}
```

可以考虑删除的文件：

```text
~/datasets/sift.tar.gz
```

因为解压后压缩包通常不是必须保留。

高风险提醒：下面命令会删除文件，确认不需要压缩包后再运行。

```bash
rm ~/datasets/sift.tar.gz
```

不建议现在删除：

```text
~/ann_exp/log
~/ann_exp/result
~/ann_exp/figures
```

这些是报告证据。

---

## 24. 现在最小下一步

你现在应该先执行：

运行位置：**Windows PowerShell**

```powershell
Get-PSDrive -PSProvider FileSystem |
Select Name,Root,@{n="FreeGB";e={[math]::Round($_.Free/1GB,1)}},@{n="UsedGB";e={[math]::Round($_.Used/1GB,1)}}
```

然后在 WSL 中执行：

```bash
cd ~
mkdir -p ~/datasets
cd ~/datasets

wget -O sift.tar.gz ftp://ftp.irisa.fr/local/texmex/corpus/sift.tar.gz   2>&1 | tee ~/ann_exp/log/download_sift.log

ls -lh ~/datasets/sift.tar.gz
```

如果下载失败，贴：

```bash
tail -n 50 ~/ann_exp/log/download_sift.log
```

---

## 5. Continuation Manual (After Smoke Test)

> Source: `DiskANN_后续实验指导手册.md` (787 lines, 14 KB)

# DiskANN 选题二后续实验指导手册

> 适用环境：Windows + WSL2 Ubuntu-24.04  
> 当前用户：dzq  
> 当前项目目录：`/home/dzq/projects/DiskANN`  
> 当前推荐工作目录：
>
> ```bash
> ~/projects/DiskANN
> ~/datasets
> ~/ann_exp
> ```

---

## 0. 你当前已经完成了什么

根据终端记录，你已经完成：

```text
1. WSL2 Ubuntu-24.04 已安装并可进入
2. WSL 已迁移到 D:\WSL\Ubuntu-24.04
3. 默认用户已变为 dzq
4. sudo 权限已修复
5. 基础开发依赖已安装
6. libmkl-full-dev 已安装，并选择 no，不设为系统默认 BLAS/LAPACK
7. DiskANN 已 clone 到 /home/dzq/projects/DiskANN
8. clone 命令使用了 -b cpp_main
9. VS Code 通过 code . 已成功连接 WSL，并安装了 VS Code Server
```

---

## 1. 你目前是否已经切换到 cpp_main 分支

从你的终端记录看，你执行的是：

```bash
git clone --recursive -b cpp_main https://github.com/microsoft/DiskANN.git
```

所以**大概率已经在 `cpp_main` 分支**。

但最准确的确认方式是在 WSL 中执行：

```bash
cd ~/projects/DiskANN
git branch --show-current
```

如果输出：

```text
cpp_main
```

就确认无误。

也可以执行：

```bash
git status -sb
```

如果看到：

```text
## cpp_main
```

也说明当前是 cpp_main 分支。

如果不是 cpp_main，可以执行：

```bash
cd ~/projects/DiskANN
git fetch origin
git checkout cpp_main
git submodule update --init --recursive
```

---

## 2. VS Code + WSL2 使用方式

你已经执行过：

```bash
cd ~/projects/DiskANN
code .
```

终端显示：

```text
Installing VS Code Server for Linux x64
Compatibility check successful (0)
```

说明 VS Code Remote WSL 已经成功连接。

以后打开项目的推荐方式：

```bash
wsl -d Ubuntu-24.04
cd ~/projects/DiskANN
code .
```

注意 VS Code 左下角应该显示类似：

```text
WSL: Ubuntu-24.04
```

这说明你正在编辑 WSL 内部的 Linux 文件，而不是 Windows 的 `/mnt/c` 文件。

---

## 3. Claude Code / Claude 插件使用原则

如果你的 Claude Code 已经配置在 WSL 中，建议优先在 VS Code 的 WSL 终端里使用：

```bash
cd ~/projects/DiskANN
claude
```

或者在 VS Code 的 Claude Code 插件界面中打开当前 WSL 工作区。

如果使用了自定义 API，例如：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-xxx",
    "ANTHROPIC_BASE_URL": "https://api.xxx.com/anthropic",
    "ANTHROPIC_MODEL": "MiniMax-M3"
  }
}
```

建议保存到：

```bash
~/.claude/settings.json
```

如果没有 `nano`，可以安装：

```bash
sudo apt install -y nano
```

也可以不用 nano，直接用 VS Code：

```bash
code ~/.claude/settings.json
```

或者用 cat 写入：

```bash
mkdir -p ~/.claude
cat > ~/.claude/settings.json <<'EOF'
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-xxx",
    "ANTHROPIC_BASE_URL": "https://api.xxx.com/anthropic",
    "ANTHROPIC_MODEL": "MiniMax-M3",
    "API_TIMEOUT_MS": "3000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "includeCoAuthoredBy": false,
  "model": "opus"
}
EOF
```

注意：JSON 里建议把环境变量值都写成字符串，尤其是：

```json
"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
```

而不是：

```json
"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
```

写好后验证 JSON 格式：

```bash
python3 -m json.tool ~/.claude/settings.json
```

如果正常格式化输出，说明 JSON 语法没问题。

---

## 4. 总体实验路线

建议不要一开始就做三个进阶。正确路线是：

```text
阶段 1：原版 DiskANN 编译成功
阶段 2：10K 小数据 smoke test
阶段 3：SIFT1M 基础实验
阶段 4：profile 性能瓶颈分析
阶段 5：进阶三 cache 优化
阶段 6：进阶二 block 重排轻量版
阶段 7：进阶四 prefetch-lite / 异步 IO 轻量版
阶段 8：整理报告、图表、代码说明
```

其中优先级：

```text
必须完成：基础要求
优先进阶：cache 优化
次优进阶：block 重排轻量版
挑战进阶：prefetch-lite / 异步 IO
不建议优先：RaBitQ
```

---

## 5. 阶段 1：编译原版 DiskANN

进入项目：

```bash
cd ~/projects/DiskANN
```

确认分支：

```bash
git branch --show-current
```

创建 build 目录：

```bash
mkdir -p build
cd build
```

CMake 配置：

```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
```

编译并保存日志：

```bash
mkdir -p ~/ann_exp/log
make -j$(nproc) 2>&1 | tee ~/ann_exp/log/diskann_build.log
```

如果报错，查看最后 50 行：

```bash
tail -n 50 ~/ann_exp/log/diskann_build.log
```

编译成功后检查：

```bash
ls ~/projects/DiskANN/build/apps
```

希望看到：

```text
build_memory_index
search_memory_index
build_disk_index
search_disk_index
```

---

## 6. 阶段 2：建立实验目录

```bash
mkdir -p ~/ann_exp/{data,index,result,log,scripts,figures}
mkdir -p ~/datasets
```

目录用途：

```text
~/datasets       放原始数据集
~/ann_exp/data   放转换后的 fbin / u8bin / groundtruth
~/ann_exp/index  放索引
~/ann_exp/result 放搜索结果 csv / txt
~/ann_exp/log    放运行日志
~/ann_exp/scripts 放脚本
~/ann_exp/figures 放图
```

---

## 7. 阶段 3：10K smoke test

目的：不是追求性能，而是确认流程跑通。

建议先做：

```text
base vectors: 10000
query vectors: 1000
dimension: 128
```

你需要完成：

```text
1. 准备 base 数据
2. 准备 query 数据
3. 生成 groundtruth
4. 构建 memory index
5. 搜索 memory index
6. 构建 disk index
7. 搜索 disk index
8. 保存日志
```

输出文件建议命名：

```text
~/ann_exp/log/build_memory_10k.log
~/ann_exp/log/search_memory_10k_L20.log
~/ann_exp/log/build_disk_10k.log
~/ann_exp/log/search_disk_10k_L20_B2.log
```

10K 阶段的判断标准：

```text
能构建索引
能搜索
搜索结果能保存
Recall / QPS 能从日志里提取
没有路径错误
没有权限错误
```

---

## 8. 阶段 4：SIFT1M 基础实验

正式基础实验建议用 SIFT1M。

对比对象：

```text
Memory Vamana
DiskANN SSD
```

推荐参数：

```text
L = 10, 20, 40, 80, 120
beamwidth = 2
threads = 4
cache_nodes = 0
```

你最终要得到一个 CSV：

```csv
method,L,beamwidth,cache_nodes,recall@1,recall@5,recall@10,qps,mean_latency_us,p999_latency_us,max_rss_mb,mean_ios,mean_io_us,fs_inputs,fs_outputs
memory,10,0,0,...
disk,10,2,0,...
```

图表至少画：

```text
1. QPS - Recall@10 曲线
2. L - Recall@10 曲线
3. L - QPS 曲线
4. DiskANN 的 Mean IOs 随 L 变化
```

---

## 9. 阶段 5：profile 性能瓶颈分析

重点证明：

```text
DiskANN SSD 的瓶颈主要来自 SSD 随机 IO，而不是纯 CPU 计算。
```

建议统计：

```text
QPS
平均延迟
P999 延迟
Mean IOs
Mean IO time
IO 时间占比
非 IO 时间占比
Max RSS
文件系统输入 fs_inputs
文件系统输出 fs_outputs
索引文件大小
```

推荐输出：

```text
~/ann_exp/result/profile_summary_sift1m.csv
~/ann_exp/result/index_size_summary_sift1m.csv
~/ann_exp/figures/profile_io_breakdown.png
```

报告中可写的典型分析逻辑：

```text
随着搜索参数 L 增大，Recall 提升，但 QPS 下降。
DiskANN SSD 查询过程中需要访问更多磁盘节点，Mean IOs 上升。
平均延迟中 IO 时间占比很高，说明主要瓶颈是随机 IO。
因此后续优化重点放在减少 IO 次数、提高 cache 命中率、改善局部性和重叠 IO 等方面。
```

---

## 10. 阶段 6：进阶三 cache 优化

这是最推荐你做的进阶。

目标：

```text
利用查询访问热点，设计比原始 BFS cache 更适合当前 query 分布的 cache 策略。
```

建议设计自己的版本，不要完全照搬朋友的命名。

可以命名：

```text
FHC: Frequency-based Hot Cache
```

流程：

```text
1. 把 query 分成 train query 和 eval query
2. train query 用来统计热点节点
3. eval query 用来评估性能
4. 根据访问频率选择 top-k 热点节点进入 cache
5. 对比 none / bfs / hot / hybrid
```

推荐策略：

```text
none: 不使用 cache
bfs: DiskANN 原始 BFS cache
hot: 训练 query 统计出的热点 cache
hybrid: BFS cache + hot cache 混合
```

推荐参数：

```text
L = 40
beamwidth = 2
cache_nodes = 0, 5000, 10000, 20000
train query = 前 1000 条
eval query = 后 1000 条
```

输出表：

```csv
strategy,cache_nodes,L,beamwidth,recall@10,qps,mean_latency_us,mean_ios,max_rss_mb
none,0,40,2,...
bfs,5000,40,2,...
hot,5000,40,2,...
hybrid,5000,40,2,...
```

报告重点：

```text
hot cache 能减少平均 IO 次数；
cache_nodes 增大时，QPS 通常提升、延迟下降；
但 cache 会增加内存占用；
hybrid 策略可能比单一 BFS 或 hot 更稳定。
```

---

## 11. 阶段 7：进阶二 block 重排轻量版

真正修改 DiskANN 的磁盘布局比较难。建议做轻量版。

目标：

```text
用训练 query 的访问路径统计节点共现关系，模拟把经常连续访问的节点放入同一个 4KB block。
```

实现流程：

```text
1. 收集搜索访问序列
2. 统计节点之间的连续共现次数
3. 根据共现频率做 greedy grouping
4. 生成 node_id -> block_id 映射
5. 比较原始布局和重排布局下的理论 block 访问数
```

输出：

```text
平均访问 block 数
block IO reduction ratio
重排前后柱状图
```

可交付成果：

```text
~/ann_exp/scripts/block_reorder_sim.py
~/ann_exp/result/block_reorder_summary.csv
~/ann_exp/figures/block_reorder_io_reduction.png
```

报告中要诚实说明：

```text
本实验实现的是访问轨迹驱动的 block 重排模拟，用于评估局部性优化潜力；没有完全重写 DiskANN 底层磁盘文件格式。
```

如果时间不够，这个进阶可以作为“探索性进阶”。

---

## 12. 阶段 8：进阶四 prefetch-lite / 异步 IO 轻量版

真正用 `io_uring` 或大改异步 IO 难度较高。建议做轻量版：

```text
prefetch-lite：根据当前候选队列，提前读取下一批可能访问的节点。
```

思路：

```text
1. 当前轮计算距离时，观察候选队列前若干个节点
2. 提前触发这些节点的读取
3. 下一轮真正访问时，可能减少等待
4. 对比 no-prefetch 和 prefetch-lite
```

评估指标：

```text
QPS
mean_latency_us
p999_latency_us
mean_ios
mean_io_us
recall@10
```

报告中要区分：

```text
完整异步 IO
```

和：

```text
预取机制 / prefetch-lite
```

不要把轻量预取说成完整 io_uring 异步 IO。

---

## 13. 推荐的 Git 分支管理

不要直接在原始 cpp_main 上乱改。

建议：

```bash
cd ~/projects/DiskANN
git branch --show-current
git checkout -b exp-baseline
```

基础实验用 `exp-baseline`。

做 cache 时：

```bash
git checkout cpp_main
git checkout -b exp-hot-cache
```

做 block reorder 时：

```bash
git checkout cpp_main
git checkout -b exp-block-reorder
```

做 prefetch 时：

```bash
git checkout cpp_main
git checkout -b exp-prefetch-lite
```

查看当前分支：

```bash
git branch
```

保存修改：

```bash
git status
git add .
git commit -m "add hot cache experiment"
```

如果暂时不想 commit，至少用：

```bash
git diff > ~/ann_exp/log/my_changes.patch
```

保存补丁。

---

## 14. 推荐报告结构

```text
1. 引言
2. 实验环境
3. DiskANN 原理简介
4. 基础实验设计
   4.1 数据集
   4.2 参数设置
   4.3 Memory Vamana vs DiskANN SSD
   4.4 QPS-Recall 分析
5. Profile 瓶颈分析
   5.1 IO 次数
   5.2 IO 时间占比
   5.3 内存和 SSD 占用
6. 进阶优化一：热点 cache
7. 进阶优化二：block 重排模拟
8. 进阶优化三：prefetch-lite
9. 总结
10. AI 使用说明
11. 附录：运行命令和脚本
```

---

## 15. 当前最该执行的命令

现在最重要的是确认分支并编译：

```bash
cd ~/projects/DiskANN
git branch --show-current
git status -sb
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc) 2>&1 | tee ~/ann_exp/log/diskann_build.log
```

编译结束后：

```bash
ls ~/projects/DiskANN/build/apps
```

如果失败：

```bash
tail -n 50 ~/ann_exp/log/diskann_build.log
```

把最后 50 行发给我。

---

## 16. 给 Claude Code 的使用建议

你可以让 Claude Code 做：

```text
解释 DiskANN 源码结构
帮你定位 search_disk_index.cpp 参数解析位置
帮你找 cache 相关函数
帮你写日志解析脚本
帮你写 CSV 汇总脚本
帮你写 matplotlib 画图脚本
帮你整理报告段落
```

不要让 Claude Code 直接做：

```text
一次性大改底层 IO
一次性完成三个进阶
直接替换朋友的源码
直接生成整篇报告并原样提交
```

比较好的提示词：

```text
请先阅读 search_disk_index.cpp、pq_flash_index.cpp、pq_flash_index.h，
帮我找出 DiskANN SSD 搜索过程中 cache 初始化、节点读取、IO 统计相关的函数。
不要修改代码，只输出文件路径、函数名和作用说明。
```

第二步再让它小改：

```text
在不改变原有搜索结果正确性的前提下，
为 search_disk_index.cpp 增加一个 --cache_strategy 参数，
先只解析参数并打印，不改实际搜索逻辑。
```

第三步再逐步实现 hot cache。

---

## 17. 注意事项

1. 每次进入 WSL 后先执行：

```bash
cd ~
```

2. 不要在 `/mnt/c` 或 `/mnt/d` 下跑实验。

3. 所有日志都保存：

```bash
~/ann_exp/log
```

4. 所有结果都保存：

```bash
~/ann_exp/result
```

5. 所有图都保存：

```bash
~/ann_exp/figures
```

6. 每做完一个阶段，先备份：

```bash
tar -czf ~/ann_exp/log/backup_$(date +%Y%m%d_%H%M).tar.gz ~/ann_exp/scripts ~/ann_exp/result ~/ann_exp/log
```

7. 不要一开始跑 10M 数据集。

8. 不要把三个进阶一起开工。先 cache，再 block reorder，再 prefetch-lite。
