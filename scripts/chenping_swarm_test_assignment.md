# 陈平带领Kimi Swarm测试任务书

**任务派发时间**: 2026-03-27  
**负责人**: 陈平 (QA测试工程师)  
**任务性质**: 使用Kimi Swarm并行执行company-directory测试

---

## 背景
陈平需要掌握Kimi Swarm来驱动后续所有测试工作。本次任务是实战演练。

---

## 测试任务

### 测试目标
验证company-directory skill的CLI功能完整性。

### 并行测试计划（Swarm模式）

#### 子Agent 1: 成员查询测试
**负责**: 验证agent查询相关命令
```bash
cd /Users/wangrenzhu/work/MetaClaw/InfinityCompany/skills/company-directory

echo "=== 测试1: 列出所有成员 ==="
python3 cli.py agent --list

echo "=== 测试2: 查询张良信息 ==="
python3 cli.py agent zhangliang

echo "=== 测试3: 按角色筛选 ==="
python3 cli.py agent --role dev
```

#### 子Agent 2: 组织架构测试
**负责**: 验证org相关命令
```bash
cd /Users/wangrenzhu/work/MetaClaw/InfinityCompany/skills/company-directory

echo "=== 测试4: 查看组织架构 ==="
python3 cli.py org --chart

echo "=== 测试5: 查看汇报链 ==="
python3 cli.py chain hanxin

echo "=== 测试6: 查询升级路径 ==="
python3 cli.py escalation incident
```

#### 子Agent 3: 通讯功能测试
**负责**: 验证acpx和email功能
```bash
cd /Users/wangrenzhu/work/MetaClaw/InfinityCompany/skills/company-directory

echo "=== 测试7: 生成acpx命令 ==="
python3 cli.py acpx hanxin "陈平Swarm测试消息"

echo "=== 测试8: 查询联系方式 ==="
python3 cli.py contact zhoubo
```

---

## 陈平执行指南

### 方式A: 使用kimi-code-cli直接执行（推荐）
```bash
cd /Users/wangrenzhu/work/MetaClaw

kimi --yolo --message "作为陈平(QA负责人)，请并行执行以下3个测试任务：

任务1 - 成员查询测试:
执行命令测试company-directory的agent查询功能，输出结果

任务2 - 组织架构测试:  
执行命令测试company-directory的org功能，输出结果

任务3 - 通讯功能测试:
执行命令测试company-directory的acpx/contact功能，输出结果

汇总所有测试结果，生成测试报告。" --max-turns 20
```

### 方式B: 手动分步执行
如果方式A超时，陈平可以手动执行：
```bash
# 自行创建3个测试脚本，分别执行，然后汇总结果
```

---

## 验收标准

陈平完成后需要：
1. ✅ 执行上述至少6个测试用例
2. ✅ 生成测试报告文件：`/Users/wangrenzhu/work/MetaClaw/test_report_chenping_swarm.md`
3. ✅ 通过acpx通知韩信：
   ```
   acpx hanxin "陈平完成Swarm测试，报告路径:test_report_chenping_swarm.md"
   ```

---

## 状态追踪

| 检查项 | 状态 | 时间 |
|--------|------|------|
| 任务派发 | ⏳ 已发送 | 2026-03-27 |
| 陈平确认 | ⏳ 等待 | - |
| 测试执行 | ⏳ 等待 | - |
| 报告提交 | ⏳ 等待 | - |

---

**备注**: 陈平遇到技术问题可随时通过acpx联系韩信协助。
