# DLT 文件处理脚本 & MCU 日志处理脚本

本 README 文件旨在介绍如何使用提供的 Python 脚本来处理 .dlt 文件并提取错误日志。

## 脚本功能概述

### DLT 处理脚本

该脚本主要完成以下任务：

1. **处理指定文件夹中的 .dlt 文件**：查找文件名包含 `PARK` 的 .dlt 文件并将其转换为 .txt 文件。
2. **解压最接近指定时间的 .tar 文件**：在历史文件夹中查找最接近目标时间的 .tar 文件并进行解压。
3. **检查解压文件夹中的文件**：查找解压后文件夹中的 .dlt 文件，并在满足一定条件时修改文件后缀。
4. **记录错误日志**：遍历指定文件夹中的 .txt 文件，将目标时间之前的错误信息记录到 `failure.txt` 文件中。

### MCU 日志处理脚本

该脚本的主要功能如下：

1. **读取日志文件**：从指定的 MCU 日志文件路径中读取日志文件。
2. **提取错误日志**：提取在给定时间之前的 `ErrorManager` 错误日志条目。
3. **写入错误日志**：将提取的错误日志条目写入指定的输出文件中。

## 使用说明

### 环境要求

- Python 3.x
- 需要安装的库：pip install -r requirements.txt

### 运行脚本

#### DLT 处理脚本

脚本接受一个参数，即目标时间，格式为 `YYYY/MM/DD - HH:MM:SS`。请按以下格式运行脚本：

```bash
python dlt_parser.py '2024/04/15 - 14:08:03'
```

#### MCU 日志处理脚本

脚本接受一个参数，即错误时间，格式为 `YYYY/MM/DD - HH:MM:SS`。请按以下格式运行脚本：

```bash
python MCUlog_parser.py '2024/04/15 - 15:31:03'
```