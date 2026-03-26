# OpenViking Skill 安装指南

> OpenViking 是一个记忆增强技能，用于 AI Agent 的长期记忆存储与检索。
> 
> **设计理念**：Notion 为主（看板状态、任务进度），OpenViking 为辅（历史上下文、决策依据、技术方案）。

---

## 目录

1. [安装前准备](#1-安装前准备)
2. [快速安装](#2-快速安装)
3. [配置详解](#3-配置详解)
4. [与 Notion 联动配置](#4-与-notion-联动配置)
5. [备份与恢复](#5-备份与恢复)
6. [故障排查](#6-故障排查)
7. [卸载](#7-卸载)

---

## 1. 安装前准备

### 1.1 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| Python | 3.9+ | 3.11+ |
| 内存 | 2GB | 4GB+ |
| 磁盘空间 | 1GB | 5GB+ |
| 操作系统 | Linux/macOS/Windows WSL | macOS / Linux |

### 1.2 依赖库

```bash
# 核心依赖
pip install notion-client>=2.0.0
pip install pyyaml>=6.0
pip install schedule>=1.2.0

# 向量数据库（可选）
pip install chromadb>=0.4.0

# 日志与工具
pip install python-dotenv>=1.0.0
pip install click>=8.0.0
```

### 1.3 Notion Integration 创建步骤

#### 步骤 1：访问 Notion Integrations 页面

1. 打开浏览器，访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 使用你的工作区账号登录

#### 步骤 2：创建新的 Integration

1. 点击右上角 **"New integration"** 按钮
2. 填写基本信息：
   - **Name**: `OpenViking Memory`
   - **Associated workspace**: 选择你的工作区
   - **Type**: 选择 `Internal`（内部使用）
   - **Logo**: 可选，可上传自定义图标

3. 点击 **"Submit"** 创建

#### 步骤 3：配置权限

在 Integration 详情页，配置以下权限：

| 权限类型 | 需要的权限 | 说明 |
|---------|-----------|------|
| Content Capabilities | Read content | 读取数据库内容 |
| Content Capabilities | Insert content | 创建新记录 |
| Content Capabilities | Update content | 更新现有记录 |
| User Capabilities | No user information | 不需要用户信息 |

#### 步骤 4：获取 API Key

1. 在 Integration 详情页，找到 **"Internal Integration Token"** 区域
2. 点击 **"Show"** 按钮显示 Token
3. 点击复制按钮复制 Token
4. **⚠️ 重要**：将此 Token 保存到安全位置，它只会显示一次

示例 Token 格式：
```
<YOUR_NOTION_API_KEY>
```

#### 步骤 5：将 Integration 关联到数据库

1. 打开你的 Notion 工作区
2. 导航到需要关联的数据库页面
3. 点击数据库页面右上角的 **"..."**（更多选项）
4. 选择 **"Add connections"**
5. 搜索并选择你创建的 `OpenViking Memory` Integration
6. 点击 **"Confirm"** 确认

**需要对以下数据库重复此操作**：
- 外部需求看板
- 需求看板
- 迭代看板
- Bug 看板
- 每日复盘

---

## 2. 快速安装

### 2.1 安装方式一：pip 安装（推荐）

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装 OpenViking Skill
pip install openviking-skill

# 验证安装
openviking --version
```

### 2.2 安装方式二：源码安装

```bash
# 克隆仓库
git clone https://github.com/infinitycompany/openviking-skill.git
cd openviking-skill

# 安装依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .

# 验证安装
python -m openviking --version
```

### 2.3 配置文件初始化

```bash
# 创建配置目录
mkdir -p ~/.config/openviking

# 复制配置模板
cp config.template.yaml ~/.config/openviking/config.yaml

# 编辑配置文件
nano ~/.config/openviking/config.yaml
# 或
vim ~/.config/openviking/config.yaml
```

### 2.4 验证安装成功

```bash
# 运行诊断检查
openviking doctor

# 预期输出：
# ✅ Python version: 3.11.0
# ✅ Notion API: Connected
# ✅ Config file: Found at ~/.config/openviking/config.yaml
# ✅ Storage directory: Accessible
# ✅ Vector DB: Ready (optional)
```

**手动验证测试**：

```python
# test_installation.py
from openviking import OpenVikingClient

# 初始化客户端
client = OpenVikingClient()

# 测试连接
result = client.ping()
print(f"连接状态: {result}")

# 测试记忆存储
client.memory.store(
    category="test",
    content="安装测试",
    metadata={"source": "installation"}
)

print("✅ OpenViking 安装验证成功！")
```

---

## 3. 配置详解

### 3.1 配置文件位置

| 操作系统 | 默认配置路径 |
|---------|-------------|
| Linux | `~/.config/openviking/config.yaml` |
| macOS | `~/.config/openviking/config.yaml` |
| Windows | `%APPDATA%\openviking\config.yaml` |

### 3.2 Notion 数据库 ID 配置

#### 获取数据库 ID

**方法 1：从 URL 获取**

1. 打开 Notion 数据库页面
2. 复制浏览器地址栏中的 URL
3. 提取数据库 ID（32 字符的字符串）

```
URL 示例：
https://www.notion.so/workspace/12345678-1234-1234-1234-123456789abc?v=...

数据库 ID：
12345678-1234-1234-1234-123456789abc
```

**方法 2：使用 OpenViking CLI**

```bash
# 列出可访问的数据库
openviking notion list-databases

# 输出示例：
# 📚 外部需求看板: a1b2c3d4-e5f6-7890-abcd-ef1234567890
# 📚 需求看板: b2c3d4e5-f6a7-8901-bcde-f12345678901
```

#### 配置数据库映射

编辑 `config.yaml`：

```yaml
notion:
  databases:
    external_requirements: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    requirements: "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    iteration: "c3d4e5f6-a7b8-9012-cdef-123456789012"
    bug_tracking: "d4e5f6a7-b8c9-0123-defa-234567890123"
    retrospective: "e5f6a7b8-c9d0-1234-efab-345678901234"
```

### 3.3 OpenViking 存储路径配置

```yaml
storage:
  # 本地存储路径（支持相对路径和绝对路径）
  local_path: "./data/openviking"
  
  # 或使用绝对路径
  # local_path: "/var/lib/openviking"
  # local_path: "/Users/yourname/Documents/openviking"
```

**目录结构**：

```
./data/openviking/
├── memories/           # 原始记忆数据
│   ├── 2024/
│   │   ├── 01/
│   │   └── 02/
│   └── index.json
├── vectors/            # 向量索引
│   └── chroma/
├── cache/              # 缓存文件
└── metadata.db         # SQLite 元数据
```

### 3.4 同步规则配置

```yaml
notion:
  sync:
    enabled: true
    interval_minutes: 60      # 自动同步间隔（分钟）
    batch_size: 100           # 每批处理记录数
    conflict_resolution: "notion_wins"  # 冲突解决策略
    
    # 同步的字段映射
    field_mapping:
      title: "Name"
      status: "Status"
      priority: "Priority"
      assignee: "Assignee"
      created_at: "Created time"
      updated_at: "Last edited time"
```

**冲突解决策略**：

| 策略 | 说明 |
|-----|------|
| `notion_wins` | Notion 数据优先（默认） |
| `openviking_wins` | OpenViking 数据优先 |
| `timestamp_wins` | 时间戳最新的优先 |
| `manual` | 手动解决冲突 |

### 3.5 日志级别配置

```yaml
logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  file: "./logs/openviking.log"
  max_size_mb: 10            # 单个日志文件最大大小
  backup_count: 5            # 保留的备份文件数
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**日志级别说明**：

| 级别 | 用途 | 日志量 |
|-----|------|-------|
| DEBUG | 开发调试 | 大量 |
| INFO | 正常运行信息（推荐） | 中等 |
| WARNING | 警告信息 | 较少 |
| ERROR | 错误信息 | 最少 |

---

## 4. 与 Notion 联动配置

### 4.1 数据库关联映射

OpenViking 需要与 Notion 的多个数据库建立关联：

```yaml
notion:
  # 数据库 ID 映射
  databases:
    # 外部需求看板 - 存储外部客户/合作伙伴的需求
    external_requirements: ""
    
    # 需求看板 - 内部需求管理
    requirements: ""
    
    # 迭代看板 - Sprint/Iteration 管理
    iteration: ""
    
    # Bug 看板 - 缺陷跟踪
    bug_tracking: ""
    
    # 每日复盘 - 团队复盘记录
    retrospective: ""
```

### 4.2 字段映射规则

根据 Notion 数据库的实际字段名称，配置映射规则：

```yaml
notion:
  sync:
    # 通用字段映射
    field_mapping:
      # OpenViking 字段: Notion 字段
      title: "Name"
      status: "Status"
      priority: "Priority"
      assignee: "Assignee"
      tags: "Tags"
      description: "Description"
      created_at: "Created time"
      updated_at: "Last edited time"
    
    # 按数据库自定义映射
    database_mapping:
      bug_tracking:
        severity: "Severity"
        root_cause: "Root Cause"
        solution: "Solution"
      retrospective:
        date: "Date"
        participants: "Participants"
        key_learnings: "Key Learnings"
```

### 4.3 自动同步配置

```yaml
notion:
  sync:
    enabled: true
    interval_minutes: 60
    
    # 同步方向
    direction: "bidirectional"  # bidirectional, notion_to_openviking, openviking_to_notion
    
    # 增量同步配置
    incremental: true
    last_sync_timestamp: ""  # 自动维护，无需手动修改
    
    # 同步过滤器
    filters:
      status:
        include: ["In Progress", "Done", "Review"]
        exclude: ["Archived"]
      updated_within_days: 30  # 只同步最近 30 天更新的记录
```

### 4.4 Webhook 配置（可选）

如需实时同步，可配置 Notion Webhook：

```yaml
notion:
  sync:
    webhook_url: "https://your-server.com/webhook/notion"
    webhook_secret: "your_webhook_secret"
```

**设置步骤**：

1. 在 Notion Integration 页面启用 Webhook
2. 配置 Webhook URL 指向你的服务器
3. 在服务器端配置 OpenViking Webhook 处理器

```python
# webhook_handler.py
from flask import Flask, request
from openviking import SyncManager

app = Flask(__name__)
sync_manager = SyncManager()

@app.route('/webhook/notion', methods=['POST'])
def handle_notion_webhook():
    data = request.json
    sync_manager.handle_webhook(data)
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 5. 备份与恢复

### 5.1 备份策略

```yaml
storage:
  backup:
    enabled: true
    schedule: "0 2 * * *"      # 每天凌晨 2 点备份（Cron 表达式）
    retention_days: 30         # 保留 30 天的备份
    backup_path: "./backups/openviking"
    compression: true          # 启用压缩
    encrypt: false             # 启用加密（可选）
```

### 5.2 手动备份

```bash
# 执行完整备份
openviking backup create --name "manual-backup-$(date +%Y%m%d)"

# 备份输出：
# ✅ 备份创建成功: ./backups/openviking/manual-backup-20240115.tar.gz
# 📦 大小: 15.2 MB
# 📁 包含: memories/, vectors/, metadata.db, config.yaml
```

### 5.3 定时备份脚本

创建备份脚本 `/etc/cron.daily/openviking-backup`：

```bash
#!/bin/bash

# OpenViking 自动备份脚本
BACKUP_DIR="/var/backups/openviking"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 创建备份
openviking backup create \
  --output "$BACKUP_DIR" \
  --name "auto-$TIMESTAMP" \
  --compress

# 清理旧备份
find "$BACKUP_DIR" -name "auto-*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 发送通知（可选）
echo "OpenViking backup completed at $TIMESTAMP" | logger
```

设置权限：

```bash
chmod +x /etc/cron.daily/openviking-backup
```

### 5.4 数据导出方法

```bash
# 导出所有记忆为 JSON
openviking export --format json --output ./export/memories.json

# 导出特定类别
openviking export --category tech_design --format markdown --output ./export/tech/

# 导出为 CSV（用于 Excel 分析）
openviking export --format csv --output ./export/memories.csv
```

### 5.5 恢复流程

#### 从备份恢复

```bash
# 列出可用备份
openviking backup list

# 输出示例：
# 📦 auto-20240115_020000.tar.gz    2024-01-15 02:00    15.2 MB
# 📦 auto-20240114_020000.tar.gz    2024-01-14 02:00    15.0 MB
# 📦 manual-backup-20240110.tar.gz  2024-01-10 10:30    14.8 MB

# 恢复指定备份
openviking backup restore auto-20240115_020000.tar.gz

# 确认恢复
# ⚠️ 这将覆盖当前数据，是否继续？ [y/N]: y
# ✅ 恢复完成
```

#### 手动恢复步骤

```bash
# 1. 停止 OpenViking 服务
systemctl stop openviking

# 2. 备份当前数据（以防万一）
cp -r ./data/openviking ./data/openviking.bak.$(date +%Y%m%d)

# 3. 解压备份
tar -xzf ./backups/openviking/auto-20240115_020000.tar.gz -C ./data/

# 4. 重启服务
systemctl start openviking

# 5. 验证恢复
openviking doctor
```

### 5.6 灾难恢复预案

#### 场景 1：数据文件损坏

```bash
# 检查数据完整性
openviking doctor --fix

# 如果无法修复，从最近备份恢复
openviking backup restore --latest
```

#### 场景 2：Notion Integration 失效

```bash
# 1. 重新创建 Integration（参见 1.3 节）
# 2. 更新 API Key
openviking config set notion.api_key "ntn_new_api_key_here"

# 3. 重新关联数据库
openviking notion relink-databases

# 4. 执行全量同步
openviking sync --full
```

#### 场景 3：完全重建

```bash
# 1. 保留配置文件
cp ~/.config/openviking/config.yaml ~/config.yaml.backup

# 2. 重新安装
pip uninstall openviking-skill
pip install openviking-skill

# 3. 恢复配置
cp ~/config.yaml.backup ~/.config/openviking/config.yaml

# 4. 从备份恢复数据
openviking backup restore --latest

# 5. 验证
openviking doctor
```

---

## 6. 故障排查

### 6.1 常见问题 FAQ

#### Q1: "Notion API 连接失败"

**症状**：
```
Error: Failed to connect to Notion API (401 Unauthorized)
```

**解决方案**：
1. 检查 API Key 是否正确配置
   ```bash
   openviking config get notion.api_key
   ```
2. 验证 Integration 是否已关联到数据库
3. 检查 Integration 权限设置
4. 重新生成 API Key

#### Q2: "数据库 ID 无效"

**症状**：
```
Error: Database not found (404)
```

**解决方案**：
```bash
# 1. 列出可访问的数据库
openviking notion list-databases

# 2. 验证数据库 ID 格式（应为 32 字符 UUID）
# 3. 确认 Integration 已添加到该数据库
```

#### Q3: "同步失败，数据不一致"

**解决方案**：
```bash
# 1. 执行强制全量同步
openviking sync --full --force

# 2. 清除本地缓存
openviking cache clear

# 3. 重新同步
openviking sync
```

#### Q4: "向量搜索返回空结果"

**解决方案**：
1. 检查向量数据库是否启用
   ```bash
   openviking config get storage.vector_db.enabled
   ```
2. 重建向量索引
   ```bash
   openviking index rebuild
   ```

#### Q5: "存储空间不足"

**解决方案**：
```bash
# 1. 检查存储使用情况
openviking storage stats

# 2. 清理过期记忆
openviking memory cleanup --older-than 90d

# 3. 压缩备份
openviking backup compress
```

### 6.2 日志查看方法

```bash
# 查看实时日志
tail -f ./logs/openviking.log

# 查看最近 100 行
openviking logs --tail 100

# 查看特定日期的日志
openviking logs --date 2024-01-15

# 查看错误日志
openviking logs --level ERROR

# 按组件过滤
openviking logs --component sync
```

**日志文件位置**：

| 文件 | 内容 |
|-----|------|
| `openviking.log` | 主日志 |
| `sync.log` | 同步相关日志 |
| `notion.log` | Notion API 调用日志 |
| `error.log` | 错误日志 |

### 6.3 调试模式开启

```bash
# 临时开启调试模式
openviking --debug <command>

# 或设置环境变量
export OPENVIKING_DEBUG=1
openviking <command>

# 在配置中永久启用
openviking config set logging.level DEBUG
```

**调试信息包括**：
- 详细的 API 请求/响应
- SQL 查询语句
- 性能指标
- 内存使用情况

---

## 7. 卸载

### 7.1 完全卸载步骤

```bash
# 1. 停止服务
systemctl stop openviking  # 如果使用 systemd
pkill -f openviking        # 或手动终止

# 2. 卸载 Python 包
pip uninstall openviking-skill

# 3. 删除配置文件
rm -rf ~/.config/openviking

# 4. 删除数据文件（⚠️ 此操作不可恢复）
rm -rf ./data/openviking

# 5. 删除日志文件
rm -rf ./logs/openviking*

# 6. 删除备份（可选）
rm -rf ./backups/openviking
```

### 7.2 数据清理

```bash
# 安全清理（覆盖后删除）
openviking uninstall --secure

# 此操作将：
# 1. 使用随机数据覆盖存储文件
# 2. 删除所有配置文件
# 3. 清除日志文件
```

### 7.3 保留数据卸载

如需保留数据供后续重新安装使用：

```bash
# 1. 备份数据
openviking backup create --name "pre-uninstall-backup"

# 2. 卸载包
pip uninstall openviking-skill

# 3. 保留 ~/.config/openviking/ 和 ./data/openviking/
# 数据将在重新安装后自动恢复
```

---

## 附录

### A. 环境变量参考

| 变量 | 说明 | 示例 |
|-----|------|------|
| `OPENVIKING_CONFIG` | 配置文件路径 | `/etc/openviking/config.yaml` |
| `OPENVIKING_DEBUG` | 调试模式 | `1` 或 `true` |
| `NOTION_API_KEY` | Notion API Key | `ntn_...` |
| `OPENVIKING_LOG_LEVEL` | 日志级别 | `DEBUG` |

### B. 系统服务配置

创建 systemd 服务 `/etc/systemd/system/openviking.service`：

```ini
[Unit]
Description=OpenViking Memory Service
After=network.target

[Service]
Type=simple
User=openviking
WorkingDirectory=/opt/openviking
ExecStart=/opt/openviking/venv/bin/openviking server
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
systemctl enable openviking
systemctl start openviking
systemctl status openviking
```

### C. 快速参考命令

```bash
# 安装与配置
openviking install
openviking config edit
openviking doctor

# 同步
openviking sync
openviking sync --full
openviking sync --status

# 记忆管理
openviking memory store --category tech_design "内容"
openviking memory search "关键词"
openviking memory list --category decision

# 备份
openviking backup create
openviking backup list
openviking backup restore <name>

# 维护
openviking cache clear
openviking index rebuild
openviking storage cleanup
```

---

**文档版本**: v1.0  
**最后更新**: 2026-03-27  
**维护者**: InfinityCompany Team
