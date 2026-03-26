# InfinityCompany 环境验证测试方案

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档版本 | v1.0.0 |
| 编制日期 | 2026-03-27 |
| 适用范围 | InfinityCompany Overlay/Attach 部署模式 |
| 测试负责人 | 陈平 (测试工程师) |
| 审核人 | 萧何 (架构师) |

---

## 1. 测试目标与范围

### 1.1 测试目标

本测试方案旨在验证 InfinityCompany 虚拟 AI 公司通过 overlay/attach 模式部署到 OpenClaw 基座环境后的完整可用性，确保：

1. **环境配置正确性**：所有环境变量、目录结构、依赖服务配置正确
2. **部署流程可靠性**：Attach、Deploy、Rollback 流程能够稳定执行
3. **角色服务可用性**：10 个虚拟 Agent 的 IDENTITY.md 文件可正常读取
4. **外部服务连通性**：OpenClaw Gateway、ClawPanel 等依赖服务可达
5. **数据一致性**：部署和回滚操作不破坏已有数据

### 1.2 测试范围

| 范围项 | 包含 | 不包含 |
|--------|------|--------|
| 测试对象 | validate-overlay.sh, attach-openclaw.sh, deploy-overlay.sh, rollback-overlay.sh | OpenClaw 核心功能测试 |
| 配置验证 | configs/openclaw-target.*.env | OpenClaw 内部配置 |
| 目录结构 | overlay/, snapshots/, agents/ | 业务代码功能 |
| 服务连通 | Gateway HTTP 接口, ClawPanel Web UI | 性能测试、压力测试 |
| 角色验证 | IDENTITY.md 可读性 | Agent 推理能力 |
| 数据验证 | 快照创建/恢复 | 数据库迁移测试 |

---

## 2. 测试环境要求

### 2.1 前置条件

| 序号 | 前置条件 | 检查命令 |
|------|----------|----------|
| 1 | macOS/Linux 操作系统 | `uname -a` |
| 2 | Bash 4.0+ | `bash --version` |
| 3 | Python 3.8+ | `python3 --version` |
| 4 | rsync 已安装 | `rsync --version` |
| 5 | curl 已安装 | `curl --version` |
| 6 | OpenClaw CLI 已安装 | `which openclaw` |
| 7 | Docker & Docker Compose | `docker --version && docker-compose --version` |

### 2.2 依赖服务

| 服务名 | 地址 | 用途 | 检查方式 |
|--------|------|------|----------|
| OpenClaw Gateway | http://127.0.0.1:18789 | AI 服务网关 | HTTP GET /
| ClawPanel | http://127.0.0.1:1420/ | 可视化面板 | HTTP GET /
| Notion API | https://api.notion.com | 看板数据 | API Health Check |

### 2.3 配置文件

| 配置文件 | 路径 | 说明 |
|----------|------|------|
| 环境变量模板 | `configs/openclaw-target.example.env` | 参考模板 |
| 本地环境配置 | `configs/openclaw-target.local.env` | 实际使用配置 |

### 2.4 环境变量清单

```bash
# 核心目录配置
OPENCLAW_BASE_DIR=/Users/wangrenzhu/work/MetaClaw/runtime/openclaw-base
OPENCLAW_USER_HOME=/Users/wangrenzhu/.openclaw
CLAWPANEL_DIR=/Users/wangrenzhu/work/MetaClaw/clawpanel

# Overlay 配置
OVERLAY_SOURCE_DIR=/Users/wangrenzhu/work/MetaClaw/InfinityCompany/overlay
RUNTIME_OVERLAY_DIR=/Users/wangrenzhu/work/MetaClaw/runtime/openclaw-base/.infinity-company
BACKUP_ROOT=/Users/wangrenzhu/work/MetaClaw/InfinityCompany/snapshots

# 服务地址配置
OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
CLAWPANEL_URL=http://127.0.0.1:1420/
```

---

## 3. 详细测试用例

### 3.1 环境配置验证用例

#### TC-ENV-001: 环境变量文件存在性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ENV-001 |
| **用例名称** | 环境变量配置文件存在性检查 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | 项目仓库已克隆到本地 |

**测试步骤：**
1. 检查 `configs/openclaw-target.example.env` 文件存在
2. 检查 `configs/openclaw-target.local.env` 文件存在（如不存在需复制创建）

**预期结果：**
- 步骤1：文件存在，返回 0
- 步骤2：文件存在或可成功创建，返回 0

**验证命令：**
```bash
ls -la configs/openclaw-target.example.env
ls -la configs/openclaw-target.local.env || cp configs/openclaw-target.example.env configs/openclaw-target.local.env
```

---

#### TC-ENV-002: 必需环境变量完整性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ENV-002 |
| **用例名称** | 必需环境变量完整性检查 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | TC-ENV-001 通过 |

**测试步骤：**
1. 加载环境变量文件
2. 验证以下变量非空：
   - OPENCLAW_BASE_DIR
   - OPENCLAW_USER_HOME
   - OPENCLAW_GATEWAY_URL
   - CLAWPANEL_DIR
   - OVERLAY_SOURCE_DIR
   - RUNTIME_OVERLAY_DIR
   - BACKUP_ROOT

**预期结果：**
- 所有必需变量均已定义且非空
- 脚本退出码为 0

**验证命令：**
```bash
./scripts/validate-overlay.sh configs/openclaw-target.local.env
echo "Exit code: $?"
```

---

#### TC-ENV-003: 目录结构存在性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ENV-003 |
| **用例名称** | 关键目录结构存在性检查 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | TC-ENV-002 通过 |

**测试步骤：**
1. 检查 OPENCLAW_BASE_DIR 目录存在
2. 检查 CLAWPANEL_DIR 目录存在
3. 检查 OVERLAY_SOURCE_DIR 目录存在
4. 检查 BACKUP_ROOT 目录可创建

**预期结果：**
- 所有必需目录均存在或可创建
- 脚本正常输出目录路径

**验证命令：**
```bash
./scripts/validate-overlay.sh configs/openclaw-target.local.env
```

---

#### TC-ENV-004: 环境变量输出格式验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ENV-004 |
| **用例名称** | 环境变量输出格式检查 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ENV-003 通过 |

**测试步骤：**
1. 执行 validate-overlay.sh
2. 检查输出包含以下键值对格式：
   - env_file=
   - openclaw_base_dir=
   - openclaw_user_home=
   - openclaw_gateway_url=
   - clawpanel_dir=
   - overlay_source_dir=
   - runtime_overlay_dir=
   - backup_root=

**预期结果：**
- 输出 8 行键值对
- 每行格式为 `key=value`
- 值非空

**验证命令：**
```bash
./scripts/validate-overlay.sh configs/openclaw-target.local.env | grep -c "="
```

---

### 3.2 Attach 流程验证用例

#### TC-ATT-001: 基础 Attach 流程验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ATT-001 |
| **用例名称** | 基础附着流程功能验证 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | TC-ENV 系列用例全部通过 |

**测试步骤：**
1. 确保 overlay 源目录有测试文件
2. 执行 attach-openclaw.sh
3. 验证 RUNTIME_OVERLAY_DIR 包含同步的文件

**预期结果：**
- 脚本退出码为 0
- 输出包含 snapshot= 路径
- 输出包含 attached_from= 和 attached_to= 路径
- 目标目录文件与源目录一致

**验证命令：**
```bash
# 准备测试文件
echo "test content" > overlay/test-file.txt

# 执行 attach
./scripts/attach-openclaw.sh configs/openclaw-target.local.env

# 验证文件同步
diff -r overlay/ /Users/wangrenzhu/work/MetaClaw/runtime/openclaw-base/.infinity-company/
```

---

#### TC-ATT-002: 首次 Attach 快照创建验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ATT-002 |
| **用例名称** | 首次附着时快照目录创建验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ATT-001 通过，RUNTIME_OVERLAY_DIR 为空 |

**测试步骤：**
1. 清空 RUNTIME_OVERLAY_DIR
2. 执行 attach-openclaw.sh
3. 验证快照目录创建（即使为空）

**预期结果：**
- 快照目录以 `attach-YYYYMMDD-HHMMSS` 格式创建
- 目录存在且为空（首次 attach）

**验证命令：**
```bash
rm -rf ${RUNTIME_OVERLAY_DIR}/*
output=$(./scripts/attach-openclaw.sh configs/openclaw-target.local.env)
snapshot_dir=$(echo "$output" | grep "snapshot=" | cut -d= -f2)
ls -la "$snapshot_dir"
```

---

#### TC-ATT-003: 增量 Attach 快照备份验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ATT-003 |
| **用例名称** | 增量附着时历史数据快照备份验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ATT-001 通过，RUNTIME_OVERLAY_DIR 已有数据 |

**测试步骤：**
1. 在 RUNTIME_OVERLAY_DIR 创建历史数据文件
2. 修改 overlay 源目录文件
3. 执行 attach-openclaw.sh
4. 验证历史数据被备份到快照

**预期结果：**
- 新快照包含历史 RUNTIME_OVERLAY_DIR 的全部内容
- 新文件被正确同步到 RUNTIME_OVERLAY_DIR

**验证命令：**
```bash
# 创建历史数据
echo "historical data" > ${RUNTIME_OVERLAY_DIR}/historical.txt

# 修改源目录
echo "new content" >> overlay/test-file.txt

# 执行 attach
./scripts/attach-openclaw.sh configs/openclaw-target.local.env

# 验证快照包含历史数据
latest_snapshot=$(ls -t ${BACKUP_ROOT} | head -1)
cat ${BACKUP_ROOT}/${latest_snapshot}/historical.txt
```

---

#### TC-ATT-004: Attach 文件同步完整性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ATT-004 |
| **用例名称** | 文件同步完整性和删除一致性验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ATT-001 通过 |

**测试步骤：**
1. 在 overlay 源目录创建多个文件和子目录
2. 执行首次 attach
3. 删除源目录中部分文件
4. 执行再次 attach
5. 验证目标目录与源目录完全一致（包括删除）

**预期结果：**
- 目标目录与源目录内容完全一致
- 源目录删除的文件在目标目录也被删除

**验证命令：**
```bash
# 创建测试结构
mkdir -p overlay/subdir
echo "file1" > overlay/file1.txt
echo "file2" > overlay/subdir/file2.txt

# 首次 attach
./scripts/attach-openclaw.sh configs/openclaw-target.local.env

# 删除文件
rm overlay/file1.txt

# 再次 attach
./scripts/attach-openclaw.sh configs/openclaw-target.local.env

# 验证一致性
diff -r overlay/ ${RUNTIME_OVERLAY_DIR}/
```

---

### 3.3 Deploy 流程验证用例

#### TC-DEP-001: 完整 Deploy 流程验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-DEP-001 |
| **用例名称** | 完整部署流程功能验证 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | TC-ATT 系列用例全部通过 |

**测试步骤：**
1. 执行 deploy-overlay.sh
2. 验证 attach 流程已执行
3. 验证部署标记文件创建

**预期结果：**
- 脚本退出码为 0
- 输出包含 deployed_overlay= 路径
- 输出包含 gateway_url= 地址

**验证命令：**
```bash
./scripts/deploy-overlay.sh configs/openclaw-target.local.env
echo "Exit code: $?"
```

---

#### TC-DEP-002: 部署时间戳记录验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-DEP-002 |
| **用例名称** | 部署时间戳记录准确性验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-DEP-001 通过 |

**测试步骤：**
1. 记录当前时间
2. 执行 deploy-overlay.sh
3. 检查 last-deploy.txt 文件内容
4. 验证时间戳格式为 ISO 8601 UTC

**预期结果：**
- `${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt` 存在
- 内容为 UTC 时间格式 `YYYY-MM-DDTHH:MM:SSZ`
- 时间与实际部署时间误差 < 60 秒

**验证命令：**
```bash
./scripts/deploy-overlay.sh configs/openclaw-target.local.env
cat ${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt
```

---

#### TC-DEP-003: 部署 Gateway URL 记录验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-DEP-003 |
| **用例名称** | 部署 Gateway URL 记录验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-DEP-001 通过 |

**测试步骤：**
1. 执行 deploy-overlay.sh
2. 检查 gateway-url.txt 文件内容
3. 验证 URL 与环境变量一致

**预期结果：**
- `${RUNTIME_OVERLAY_DIR}/.release/gateway-url.txt` 存在
- 内容与 OPENCLAW_GATEWAY_URL 环境变量一致

**验证命令：**
```bash
./scripts/deploy-overlay.sh configs/openclaw-target.local.env
cat ${RUNTIME_OVERLAY_DIR}/.release/gateway-url.txt
```

---

#### TC-DEP-004: Deploy 幂等性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-DEP-004 |
| **用例名称** | 重复部署幂等性验证 |
| **优先级** | P2 (中) |
| **前置条件** | TC-DEP-001 通过 |

**测试步骤：**
1. 首次执行 deploy-overlay.sh
2. 记录首次部署时间戳
3. 再次执行 deploy-overlay.sh
4. 验证部署成功且时间戳更新

**预期结果：**
- 两次部署均成功（退出码 0）
- 第二次部署时间戳晚于第一次
- overlay 内容保持一致

**验证命令：**
```bash
./scripts/deploy-overlay.sh configs/openclaw-target.local.env
first_time=$(cat ${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt)
sleep 2
./scripts/deploy-overlay.sh configs/openclaw-target.local.env
second_time=$(cat ${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt)
[[ "$second_time" > "$first_time" ]] && echo "PASS" || echo "FAIL"
```

---

### 3.4 Rollback 流程验证用例

#### TC-ROL-001: 指定快照回滚验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ROL-001 |
| **用例名称** | 指定快照回滚功能验证 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | TC-ATT-003 通过，存在至少一个快照 |

**测试步骤：**
1. 确定要回滚的快照目录
2. 在 RUNTIME_OVERLAY_DIR 创建新文件
3. 执行 rollback-overlay.sh 指定该快照
4. 验证回滚后内容

**预期结果：**
- 脚本退出码为 0
- 输出包含 rolled_back_from= 和 rolled_back_to= 路径
- RUNTIME_OVERLAY_DIR 内容与快照一致

**验证命令：**
```bash
# 获取最新快照
snapshot=$(ls -t ${BACKUP_ROOT} | head -1)

# 创建新文件
echo "new data" > ${RUNTIME_OVERLAY_DIR}/newfile.txt

# 执行回滚
./scripts/rollback-overlay.sh configs/openclaw-target.local.env ${BACKUP_ROOT}/${snapshot}
echo "Exit code: $?"

# 验证新文件不存在
[[ ! -f ${RUNTIME_OVERLAY_DIR}/newfile.txt ]] && echo "PASS" || echo "FAIL"
```

---

#### TC-ROL-002: 自动最新快照回滚验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ROL-002 |
| **用例名称** | 自动选择最新快照回滚验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ROL-001 通过，存在多个快照 |

**测试步骤：**
1. 创建多个快照（执行多次 attach）
2. 修改 RUNTIME_OVERLAY_DIR 内容
3. 执行 rollback-overlay.sh 不指定快照参数
4. 验证回滚到最新快照

**预期结果：**
- 脚本自动选择最新的快照目录
- 回滚后内容与最新快照一致

**验证命令：**
```bash
# 创建多个快照
echo "v1" > overlay/version.txt
./scripts/attach-openclaw.sh configs/openclaw-target.local.env

echo "v2" > overlay/version.txt
./scripts/attach-openclaw.sh configs/openclaw-target.local.env

# 修改当前状态
echo "modified" > ${RUNTIME_OVERLAY_DIR}/version.txt

# 自动回滚
./scripts/rollback-overlay.sh configs/openclaw-target.local.env

# 验证回滚到 v2
cat ${RUNTIME_OVERLAY_DIR}/version.txt
```

---

#### TC-ROL-003: 回滚数据一致性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ROL-003 |
| **用例名称** | 回滚后数据一致性验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ROL-001 通过 |

**测试步骤：**
1. 创建包含多个文件和子目录的快照
2. 修改 RUNTIME_OVERLAY_DIR（添加、删除、修改文件）
3. 执行回滚
4. 使用 diff 验证数据完全一致

**预期结果：**
- diff -r 命令返回空（无差异）
- 所有文件权限、时间戳保持一致

**验证命令：**
```bash
snapshot=$(ls -t ${BACKUP_ROOT} | head -1)
./scripts/rollback-overlay.sh configs/openclaw-target.local.env ${BACKUP_ROOT}/${snapshot}
diff -r ${BACKUP_ROOT}/${snapshot}/ ${RUNTIME_OVERLAY_DIR}/
[[ $? -eq 0 ]] && echo "PASS" || echo "FAIL"
```

---

#### TC-ROL-004: 无效快照回滚失败验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ROL-004 |
| **用例名称** | 无效快照目录回滚失败处理验证 |
| **优先级** | P2 (中) |
| **前置条件** | TC-ROL-001 通过 |

**测试步骤：**
1. 执行 rollback-overlay.sh 指定不存在的目录
2. 验证脚本正确处理错误

**预期结果：**
- 脚本退出码非 0
- 输出错误信息："snapshot dir not found"

**验证命令：**
```bash
./scripts/rollback-overlay.sh configs/openclaw-target.local.env /nonexistent/snapshot
echo "Exit code: $?"
```

---

### 3.5 角色可用性验证用例

#### TC-ROL-005: 角色 IDENTITY 文件存在性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ROL-005 |
| **用例名称** | 全部 10 个 Agent IDENTITY.md 存在性验证 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | 项目仓库已克隆 |

**测试步骤：**
1. 检查以下角色的 IDENTITY.md 文件存在：
   - 张良(zhangliang) - 产品经理
   - 萧何(xiaohe) - 架构师
   - 韩信(hanxin) - 全栈研发
   - 陈平(chenping) - 测试工程师
   - 周勃(zhoubo) - 运维工程师
   - 曹参(caocan) - PMO
   - 郦食其(lishiyi) - 外部助理
   - 陆贾(lujia) - 知识库管理员
   - 叔孙通(shusuntong) - 设计师
   - 夏侯婴(xiahouying) - 私人助理

**预期结果：**
- 所有 10 个 IDENTITY.md 文件均存在
- 每个文件非空

**验证命令：**
```bash
roles=(zhangliang xiaohe hanxin chenping zhoubo caocan lishiyi lujia shusuntong xiahouying)
for role in "${roles[@]}"; do
  if [[ -f "agents/${role}/IDENTITY.md" && -s "agents/${role}/IDENTITY.md" ]]; then
    echo "✓ ${role}"
  else
    echo "✗ ${role} MISSING"
  fi
done
```

---

#### TC-ROL-006: 角色 IDENTITY 文件格式验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ROL-006 |
| **用例名称** | IDENTITY.md YAML Frontmatter 格式验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ROL-005 通过 |

**测试步骤：**
1. 读取每个角色的 IDENTITY.md
2. 验证包含有效的 YAML Frontmatter（--- 包围）
3. 验证包含 name 字段
4. 验证包含 description 字段

**预期结果：**
- 所有文件包含有效的 YAML Frontmatter
- 所有文件包含 name 和 description 字段

**验证命令：**
```bash
roles=(zhangliang xiaohe hanxin chenping zhoubo caocan lishiyi lujia shusuntong xiahouying)
for role in "${roles[@]}"; do
  file="agents/${role}/IDENTITY.md"
  if head -1 "$file" | grep -q "^---$" && grep -q "^name:" "$file" && grep -q "^description:" "$file"; then
    echo "✓ ${role} format valid"
  else
    echo "✗ ${role} format invalid"
  fi
done
```

---

#### TC-ROL-007: 角色信息可解析性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-ROL-007 |
| **用例名称** | 角色信息 YAML 可解析性验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ROL-006 通过 |

**测试步骤：**
1. 使用 Python 解析每个 IDENTITY.md 的 YAML Frontmatter
2. 验证解析成功
3. 验证 name 值与目录名一致

**预期结果：**
- 所有文件 YAML Frontmatter 可被正确解析
- name 字段值与 agents/ 下的目录名一致

**验证命令：**
```bash
python3 << 'PYEOF'
import yaml
import glob
import re
from pathlib import Path

for file in glob.glob("agents/*/IDENTITY.md"):
    content = Path(file).read_text()
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            data = yaml.safe_load(match.group(1))
            role = Path(file).parent.name
            if data.get('name') == role:
                print(f"✓ {role}: parsed, name matches")
            else:
                print(f"✗ {role}: name mismatch ({data.get('name')})")
        except Exception as e:
            print(f"✗ {file}: parse error - {e}")
    else:
        print(f"✗ {file}: no frontmatter")
PYEOF
```

---

### 3.6 Notion 集成验证用例

#### TC-NOT-001: Notion 配置文档完整性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-NOT-001 |
| **用例名称** | Notion 配置文档完整性验证 |
| **优先级** | P1 (高) |
| **前置条件** | 项目仓库已克隆 |

**测试步骤：**
1. 检查 notion/ 目录下所有角色配置文档存在
2. 验证 README.md 存在

**预期结果：**
- 10 个角色配置文档 + README.md 共 11 个文件存在
- notion/README.md 包含完整的使用说明

**验证命令：**
```bash
ls notion/*.md | wc -l
cat notion/README.md | head -20
```

---

#### TC-NOT-002: Notion API 连通性验证（可选）

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-NOT-002 |
| **用例名称** | Notion API 连通性验证 |
| **优先级** | P2 (中) |
| **前置条件** | 具有有效的 NOTION_API_TOKEN 环境变量 |

**测试步骤：**
1. 检查 NOTION_API_TOKEN 环境变量
2. 发送 Health Check 请求到 Notion API
3. 验证返回 200 OK

**预期结果：**
- API 返回状态码 200
- 响应包含有效的 JSON

**验证命令：**
```bash
if [[ -n "${NOTION_API_TOKEN:-}" ]]; then
  curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer ${NOTION_API_TOKEN}" \
    -H "Notion-Version: 2022-06-28" \
    https://api.notion.com/v1/users/me
else
  echo "SKIP: NOTION_API_TOKEN not set"
fi
```

---

### 3.7 OpenClaw Gateway 连通性验证用例

#### TC-GWY-001: Gateway 端口连通性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-GWY-001 |
| **用例名称** | OpenClaw Gateway 端口连通性验证 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | OpenClaw Gateway 服务已启动 |

**测试步骤：**
1. 从环境变量获取 Gateway URL
2. 提取主机和端口
3. 使用 nc/telnet 测试端口连通性

**预期结果：**
- 端口可连接（TCP 连接成功）
- 无连接超时或拒绝

**验证命令：**
```bash
python3 << 'PYEOF'
import socket
from urllib.parse import urlparse

url = "http://127.0.0.1:18789"  # 从环境变量读取
parsed = urlparse(url)
host = parsed.hostname or "127.0.0.1"
port = parsed.port or 80

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
try:
    sock.connect((host, port))
    print(f"✓ Gateway {host}:{port} is reachable")
except Exception as e:
    print(f"✗ Gateway {host}:{port} unreachable: {e}")
finally:
    sock.close()
PYEOF
```

---

#### TC-GWY-002: Gateway HTTP API 响应验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-GWY-002 |
| **用例名称** | Gateway HTTP API 响应验证 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | TC-GWY-001 通过 |

**测试步骤：**
1. 发送 HTTP GET 请求到 Gateway URL
2. 验证响应状态码
3. 验证响应内容为有效 JSON

**预期结果：**
- HTTP 状态码为 200
- 响应包含有效 JSON 数据

**验证命令：**
```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:18789
curl -s http://127.0.0.1:18789 | python3 -m json.tool > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

---

#### TC-GWY-003: Gateway Token 有效性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-GWY-003 |
| **用例名称** | Gateway Token 有效性验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-GWY-002 通过，~/.openclaw/openclaw.json 存在 |

**测试步骤：**
1. 读取 ~/.openclaw/openclaw.json
2. 提取 gateway.auth.token
3. 验证 token 非空且有效

**预期结果：**
- Token 可从配置文件中读取
- Token 非空字符串

**验证命令：**
```bash
python3 << 'PYEOF'
import json
from pathlib import Path

config_path = Path.home() / ".openclaw" / "openclaw.json"
if config_path.exists():
    data = json.loads(config_path.read_text())
    token = data.get("gateway", {}).get("auth", {}).get("token", "")
    if token:
        print(f"✓ Token retrieved (length: {len(token)})")
    else:
        print("✗ Token is empty")
else:
    print(f"✗ Config file not found: {config_path}")
PYEOF
```

---

### 3.8 ClawPanel 可用性验证用例

#### TC-PAN-001: ClawPanel HTTP 服务可用性验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-PAN-001 |
| **用例名称** | ClawPanel HTTP 服务可用性验证 |
| **优先级** | P0 (阻塞级) |
| **前置条件** | ClawPanel Docker 容器已启动 |

**测试步骤：**
1. 发送 HTTP GET 请求到 ClawPanel URL
2. 验证响应状态码为 200
3. 验证响应包含 HTML 内容

**预期结果：**
- HTTP 状态码为 200
- 响应内容类型为 text/html

**验证命令：**
```bash
curl -s -o /dev/null -w "HTTP %{http_code}, Content-Type: %{content_type}\n" \
  http://127.0.0.1:1420/
```

---

#### TC-PAN-002: ClawPanel 目录结构验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-PAN-002 |
| **用例名称** | ClawPanel 源代码目录结构验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-ENV-003 通过 |

**测试步骤：**
1. 检查 CLAWPANEL_DIR 目录存在
2. 检查 docker-compose.yml 或 Dockerfile 存在
3. 检查关键源代码目录存在

**预期结果：**
- CLAWPANEL_DIR 目录存在
- 包含 docker-compose.yml 或等效容器配置

**验证命令：**
```bash
CLAWPANEL_DIR="/Users/wangrenzhu/work/MetaClaw/clawpanel"
if [[ -d "$CLAWPANEL_DIR" ]]; then
  echo "✓ Directory exists"
  ls -la "$CLAWPANEL_DIR" | grep -E "docker|Dockerfile"
else
  echo "✗ Directory not found"
fi
```

---

#### TC-PAN-003: ClawPanel Docker 容器状态验证

| 属性 | 内容 |
|------|------|
| **用例ID** | TC-PAN-003 |
| **用例名称** | ClawPanel Docker 容器状态验证 |
| **优先级** | P1 (高) |
| **前置条件** | TC-PAN-002 通过，Docker 服务运行中 |

**测试步骤：**
1. 检查 ClawPanel 相关容器是否存在
2. 验证容器状态为 running
3. 验证端口映射正确（1420）

**预期结果：**
- ClawPanel 容器处于 running 状态
- 端口 1420 被正确映射

**验证命令：**
```bash
docker ps --filter "name=clawpanel" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 4. 测试执行流程

### 4.1 执行顺序

```
┌─────────────────────────────────────────────────────────────────┐
│                     测试执行流程图                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 环境准备                                               │
│  ├── TC-ENV-001  环境变量文件存在性验证                          │
│  ├── TC-ENV-002  必需环境变量完整性验证                          │
│  ├── TC-ENV-003  目录结构存在性验证                              │
│  └── TC-ENV-004  环境变量输出格式验证                            │
│                              │                                   │
│                              ▼                                   │
│  Phase 2: 基础功能验证                                           │
│  ├── TC-ATT-001  基础 Attach 流程验证                            │
│  ├── TC-ATT-002  首次 Attach 快照创建验证                        │
│  ├── TC-ATT-003  增量 Attach 快照备份验证                        │
│  └── TC-ATT-004  Attach 文件同步完整性验证                       │
│                              │                                   │
│                              ▼                                   │
│  Phase 3: 部署流程验证                                           │
│  ├── TC-DEP-001  完整 Deploy 流程验证                            │
│  ├── TC-DEP-002  部署时间戳记录验证                              │
│  ├── TC-DEP-003  部署 Gateway URL 记录验证                       │
│  └── TC-DEP-004  Deploy 幂等性验证                               │
│                              │                                   │
│                              ▼                                   │
│  Phase 4: 回滚流程验证                                           │
│  ├── TC-ROL-001  指定快照回滚验证                                │
│  ├── TC-ROL-002  自动最新快照回滚验证                            │
│  ├── TC-ROL-003  回滚数据一致性验证                              │
│  ├── TC-ROL-004  无效快照回滚失败验证                            │
│  ├── TC-ROL-005  角色 IDENTITY 文件存在性验证                    │
│  ├── TC-ROL-006  角色 IDENTITY 文件格式验证                      │
│  └── TC-ROL-007  角色信息可解析性验证                            │
│                              │                                   │
│                              ▼                                   │
│  Phase 5: 服务连通验证                                           │
│  ├── TC-NOT-001  Notion 配置文档完整性验证                       │
│  ├── TC-NOT-002  Notion API 连通性验证                           │
│  ├── TC-GWY-001  Gateway 端口连通性验证                          │
│  ├── TC-GWY-002  Gateway HTTP API 响应验证                       │
│  ├── TC-GWY-003  Gateway Token 有效性验证                        │
│  ├── TC-PAN-001  ClawPanel HTTP 服务可用性验证                   │
│  ├── TC-PAN-002  ClawPanel 目录结构验证                          │
│  └── TC-PAN-003  ClawPanel Docker 容器状态验证                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 并行/串行策略

| 测试阶段 | 执行方式 | 说明 |
|----------|----------|------|
| Phase 1: 环境准备 | **串行** | 后续测试依赖环境配置，必须顺序执行 |
| Phase 2: Attach 流程 | **串行** | 有数据依赖关系，需按序执行 |
| Phase 3: Deploy 流程 | **串行** | 依赖 Attach 完成，需顺序执行 |
| Phase 4: Rollback 流程 | **串行** | 依赖快照存在，需顺序执行 |
| Phase 5: 角色验证 | **并行** | 各角色文件独立，可并行检查 |
| Phase 5: 服务连通 | **并行** | Gateway、ClawPanel、Notion 相互独立 |

### 4.3 依赖关系

```
TC-ENV-001 ─┬─> TC-ENV-002 ─┬─> TC-ENV-003 ─┬─> TC-ENV-004
            │               │               │
            │               │               └─> TC-ATT-001 ─┬─> TC-ATT-002
            │               │                              ├─> TC-ATT-003
            │               │                              └─> TC-ATT-004
            │               │                                         │
            │               │                                         ▼
            │               │                              TC-DEP-001 ─┬─> TC-DEP-002
            │               │                                         ├─> TC-DEP-003
            │               │                                         └─> TC-DEP-004
            │               │                                         │
            │               │                                         ▼
            │               │                              TC-ROL-001 ─┬─> TC-ROL-002
            │               │                                         ├─> TC-ROL-003
            │               │                                         └─> TC-ROL-004
            │               │
            │               └──────────────────────────────────────────┬─> TC-ROL-005
            │                                                          ├─> TC-ROL-006
            │                                                          └─> TC-ROL-007
            │
            └──────────────────────────────────────────────────────────┬─> TC-NOT-001
                                                                       ├─> TC-NOT-002
                                                                       ├─> TC-GWY-001 ─┬─> TC-GWY-002 ─┬─> TC-GWY-003
                                                                       ├─> TC-PAN-001 ─┬─> TC-PAN-002 ─┬─> TC-PAN-003
```

---

## 5. 验收标准

### 5.1 通过标准

| 等级 | 要求 | 说明 |
|------|------|------|
| **完全通过** | 所有 P0/P1 用例通过，P2 用例通过率 ≥ 80% | 可上线 |
| **条件通过** | 所有 P0 用例通过，P1 用例通过率 ≥ 90% | 修复后上线 |
| **不通过** | 任一 P0 用例失败，或 P1 用例通过率 < 90% | 禁止上线 |

### 5.2 优先级定义

| 优先级 | 代号 | 定义 |
|--------|------|------|
| P0 | 阻塞级 | 失败将导致系统无法运行的核心功能 |
| P1 | 高 | 主要功能，失败将严重影响用户体验 |
| P2 | 中 | 次要功能，失败有替代方案 |
| P3 | 低 | 增强功能，失败不影响核心流程 |

### 5.3 失败分类

| 失败类型 | 定义 | 处理方式 |
|----------|------|----------|
| 配置错误 | 环境变量或路径配置错误 | 修复配置后重试 |
| 依赖缺失 | 所需服务或文件不存在 | 安装/启动依赖后重试 |
| 功能缺陷 | 脚本逻辑错误 | 修复代码后重试 |
| 环境问题 | 网络、权限等环境问题 | 排查环境后重试 |
| 预期失败 | 测试用例本身预期失败（如 TC-ROL-004） | 确认符合预期 |

### 5.4 重试策略

| 用例类型 | 重试次数 | 重试间隔 |
|----------|----------|----------|
| 环境验证 | 3 | 5秒 |
| 网络连通 | 5 | 10秒 |
| 服务启动 | 10 | 5秒 |
| 文件操作 | 2 | 1秒 |

---

## 6. 测试报告模板

### 6.1 测试执行摘要

```markdown
# InfinityCompany 环境验证测试报告

## 执行信息

| 项目 | 内容 |
|------|------|
| 报告编号 | INV-YYYYMMDD-001 |
| 执行时间 | YYYY-MM-DD HH:MM:SS |
| 执行人 | [姓名] |
| 测试环境 | [开发/测试/生产] |
| 代码版本 | [Git Commit Hash] |

## 执行摘要

| 统计项 | 数量 |
|--------|------|
| 总用例数 | 25 |
| 通过 | 23 |
| 失败 | 1 |
| 跳过 | 1 |
| 阻塞 | 0 |
| 通过率 | 92% |

## 结论

[通过 / 条件通过 / 不通过]
```

### 6.2 详细测试结果表

```markdown
## 详细测试结果

| 用例ID | 用例名称 | 优先级 | 结果 | 耗时 | 失败原因 |
|--------|----------|--------|------|------|----------|
| TC-ENV-001 | 环境变量文件存在性检查 | P0 | PASS | 0.5s | - |
| TC-ENV-002 | 必需环境变量完整性检查 | P0 | PASS | 0.3s | - |
| ... | ... | ... | ... | ... | ... |
| TC-XXX | XXXXX | P1 | FAIL | 5s | 错误详情 |
```

### 6.3 缺陷记录模板

```markdown
## 缺陷记录

### DEF-001: [缺陷标题]

| 属性 | 内容 |
|------|------|
| 关联用例 | TC-XXX |
| 严重级别 | 阻塞/严重/一般/轻微 |
| 发现时间 | YYYY-MM-DD HH:MM:SS |
| 发现人 | [姓名] |

**缺陷描述：**
[详细描述缺陷现象]

**复现步骤：**
1. [步骤1]
2. [步骤2]
3. [步骤3]

**期望结果：**
[期望的行为]

**实际结果：**
[实际的行为]

**日志/截图：**
[相关日志或截图]

**修复状态：**
- [ ] 待修复
- [ ] 修复中
- [ ] 已修复
- [ ] 已验证
```

### 6.4 输出示例

```bash
# 执行完整测试套件
./scripts/run-validation-suite.sh

# 输出示例
═══════════════════════════════════════════════════════════════
   InfinityCompany 环境验证测试
═══════════════════════════════════════════════════════════════

[Phase 1/5] 环境准备测试
───────────────────────────────────────────────────────────────
  ✓ TC-ENV-001  环境变量文件存在性检查      PASS  (0.3s)
  ✓ TC-ENV-002  必需环境变量完整性检查      PASS  (0.2s)
  ✓ TC-ENV-003  目录结构存在性检查          PASS  (0.1s)
  ✓ TC-ENV-004  环境变量输出格式检查        PASS  (0.1s)

[Phase 2/5] Attach 流程测试
───────────────────────────────────────────────────────────────
  ✓ TC-ATT-001  基础附着流程功能验证        PASS  (1.2s)
  ✓ TC-ATT-002  首次附着时快照目录创建       PASS  (0.8s)
  ✓ TC-ATT-003  增量附着时历史数据快照备份   PASS  (0.9s)
  ✓ TC-ATT-004  文件同步完整性和删除一致性   PASS  (1.1s)

[Phase 3/5] Deploy 流程测试
───────────────────────────────────────────────────────────────
  ✓ TC-DEP-001  完整部署流程功能验证        PASS  (2.5s)
  ✓ TC-DEP-002  部署时间戳记录准确性         PASS  (0.3s)
  ✓ TC-DEP-003  部署 Gateway URL 记录       PASS  (0.2s)
  ✓ TC-DEP-004  重复部署幂等性验证          PASS  (3.1s)

[Phase 4/5] Rollback 流程测试
───────────────────────────────────────────────────────────────
  ✓ TC-ROL-001  指定快照回滚功能验证        PASS  (1.5s)
  ✓ TC-ROL-002  自动选择最新快照回滚         PASS  (1.3s)
  ✓ TC-ROL-003  回滚后数据一致性验证        PASS  (0.9s)
  ✓ TC-ROL-004  无效快照回滚失败处理        PASS  (0.4s) [预期失败]
  ✓ TC-ROL-005  全部 10 个 Agent IDENTITY  PASS  (0.6s)
  ✓ TC-ROL-006  IDENTITY 格式验证           PASS  (0.8s)
  ✓ TC-ROL-007  角色信息 YAML 可解析性       PASS  (1.2s)

[Phase 5/5] 服务连通性测试
───────────────────────────────────────────────────────────────
  ✓ TC-NOT-001  Notion 配置文档完整性       PASS  (0.2s)
  - TC-NOT-002  Notion API 连通性           SKIP  (0.1s) [Token 未设置]
  ✓ TC-GWY-001  Gateway 端口连通性          PASS  (0.3s)
  ✓ TC-GWY-002  Gateway HTTP API 响应       PASS  (0.4s)
  ✓ TC-GWY-003  Gateway Token 有效性        PASS  (0.2s)
  ✓ TC-PAN-001  ClawPanel HTTP 服务         PASS  (0.5s)
  ✓ TC-PAN-002  ClawPanel 目录结构          PASS  (0.1s)
  ✓ TC-PAN-003  ClawPanel Docker 状态       PASS  (0.3s)

═══════════════════════════════════════════════════════════════
                         测试汇总
═══════════════════════════════════════════════════════════════
  总用例数: 25
  通过:     23
  失败:     0
  跳过:     1
  阻塞:     0
  ───────────────────────────────────────────────────────────
  通过率:   96%
  总耗时:   18.6s
  ───────────────────────────────────────────────────────────
  结论:  ✓ 通过 (所有 P0/P1 用例通过)
═══════════════════════════════════════════════════════════════

详细报告已保存: reports/validation-report-20260327-143022.md
```

---

## 附录

### A. 快速测试命令

```bash
# 一键执行所有验证
make validate

# 或手动执行
./scripts/validate-overlay.sh configs/openclaw-target.local.env
./scripts/attach-openclaw.sh configs/openclaw-target.local.env
./scripts/deploy-overlay.sh configs/openclaw-target.local.env
```

### B. 环境清理命令

```bash
# 清理运行时 overlay 目录
rm -rf ${RUNTIME_OVERLAY_DIR}/*

# 清理旧快照（保留最近 5 个）
cd ${BACKUP_ROOT} && ls -t | tail -n +6 | xargs rm -rf

# 完整重置
rm -rf ${RUNTIME_OVERLAY_DIR}
rm -rf ${BACKUP_ROOT}/attach-*
```

### C. 故障排查指南

| 问题 | 排查步骤 |
|------|----------|
| validate 失败 | 检查 configs/openclaw-target.local.env 是否存在且配置正确 |
| attach 失败 | 检查源目录存在且 rsync 已安装 |
| deploy 失败 | 先执行 validate 和 attach 确认前置条件满足 |
| rollback 失败 | 检查快照目录是否存在且可读 |
| Gateway 不通 | 检查 openclaw gateway status，必要时执行 openclaw gateway start |
| ClawPanel 不通 | 检查 Docker 容器状态，必要时重建 |

---

*文档版本: v1.0.0 | 最后更新: 2026-03-27 | 编制: 陈平(测试工程师)*
