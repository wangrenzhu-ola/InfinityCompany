# InfinityCompany 留痕校验策略与脚本设计

> **文档版本**: v1.0  
> **生效日期**: 2026-03-27  
> **文档维护**: 陆贾(知识库管理员) / 周勃(运维工程师)  
> **审批**: 曹参(PMO)

---

## 目录

1. [校验目标与范围](#1-校验目标与范围)
2. [Git 提交校验策略](#2-git-提交校验策略)
3. [文档更新校验策略](#3-文档更新校验策略)
4. [Notion 看板校验策略](#4-notion-看板校验策略)
5. [复盘同步校验策略](#5-复盘同步校验策略)
6. [校验脚本设计](#6-校验脚本设计)
7. [校验执行计划](#7-校验执行计划)
8. [附录：关键检查点清单](#8-附录关键检查点清单)

---

## 1. 校验目标与范围

### 1.1 校验目标

建立 InfinityCompany 全链路可追溯体系，确保：

| 目标维度 | 具体描述 | 可量化指标 |
|---------|---------|-----------|
| **完整性** | 所有协作活动均有记录 | 记录覆盖率 ≥ 98% |
| **准确性** | 记录内容真实反映实际活动 | 记录准确率 ≥ 95% |
| **时效性** | 记录与活动同步或延迟在可接受范围 | 实时记录率 ≥ 90% |
| **关联性** | 跨系统记录可相互追溯 | 关联完整率 ≥ 95% |

### 1.2 校验范围

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        InfinityCompany 留痕校验范围                          │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│   Git 代码提交    │   文档更新        │   Notion 看板    │     每日复盘       │
├──────────────────┼──────────────────┼──────────────────┼────────────────────┤
│ • 提交信息规范    │ • 修改时间戳      │ • 外部需求登记    │ • 复盘记录完整性  │
│ • 提交频率分析    │ • 版本与 Git 关联 │ • Story/Task 创建 │ • 复盘与任务关联  │
│ • 改动量统计      │ • 审批流程验证    │ • 状态流转合规    │ • 改进项跟进状态  │
│ • 分支策略合规    │ • 模板合规检查    │ • Bug 记录完整    │ • Token 开销记录  │
│ • 代码评审留痕    │ • 元数据完整性    │ • 复盘及时性      │ • 复盘周期合规    │
└──────────────────┴──────────────────┴──────────────────┴────────────────────┘
```

### 1.3 校验数据来源

| 来源系统 | 数据类型 | 访问方式 | 检查频率 |
|---------|---------|---------|---------|
| Git 仓库 | 提交日志、分支信息、Tag | `git log`, `git branch` | 实时/每日 |
| 本地文件系统 | 文档修改时间、文件哈希 | `stat`, `md5sum` | 每日 |
| Notion API | 看板记录、页面历史 | Notion REST API | 每日/每周 |
| 环境检查日志 | 每日 18:00 检查结果 | 日志文件解析 | 每日 |

---

## 2. Git 提交校验策略

### 2.1 提交信息规范检查

#### 2.1.1 提交信息格式规范

```
<type>(<scope>): <subject> [#<story-id>]

<body>

<footer>
```

**类型定义 (type)**:

| 类型 | 用途 | 适用角色 |
|-----|------|---------|
| `feat` | 新功能开发 | 韩信(研发) |
| `fix` | Bug 修复 | 韩信(研发) / 陈平(测试) |
| `docs` | 文档更新 | 陆贾(知识库) / 全员 |
| `style` | 代码格式调整 | 韩信(研发) |
| `refactor` | 代码重构 | 韩信(研发) / 萧何(架构) |
| `test` | 测试相关 | 陈平(测试) |
| `chore` | 构建/工具/配置 | 周勃(运维) |
| `design` | 设计稿更新 | 叔孙通(设计) |
| `workflow` | 流程文档更新 | 曹参(PMO) |
| `agent` | Agent 配置更新 | 夏侯婴(私人助理) |

**范围定义 (scope)**:

| 范围 | 说明 | 检查规则 |
|-----|------|---------|
| `agent/<name>` | Agent 配置更新 | 必须对应存在的 agents/*/IDENTITY.md |
| `workflow/<name>` | 流程文档更新 | 必须对应存在的 workflows/*.md |
| `skill/<name>` | 技能更新 | 必须对应存在的 skills/*/ |
| `notion/<board>` | 看板相关 | board ∈ {story,task,bug,iteration,retro} |
| `prompt/<name>` | 提示词更新 | 必须对应存在的 prompts/*.md |
| `overlay` | 运行时资产 | overlay/ 目录下文件 |
| `scripts` | 脚本更新 | scripts/ 目录下文件 |
| `configs` | 配置更新 | configs/ 目录下文件 |

#### 2.1.2 提交信息检查规则

```python
# 伪代码：提交信息检查
def check_commit_message(commit_msg: str) -> CheckResult:
    errors = []
    warnings = []
    
    # 规则1: 检查格式是否符合 Conventional Commits
    pattern = r'^(feat|fix|docs|style|refactor|test|chore|design|workflow|agent)(\([\w/-]+\))?!?: .+'
    if not re.match(pattern, commit_msg):
        errors.append("提交信息格式不符合规范")
    
    # 规则2: 检查是否关联 Story/Task ID
    if not re.search(r'#\d+', commit_msg) and not re.search(r'\[NOTION-[\w-]+\]', commit_msg):
        warnings.append("建议关联 Story/Task ID")
    
    # 规则3: 检查主题(subject)长度
    subject = extract_subject(commit_msg)
    if len(subject) > 72:
        errors.append("主题长度超过72字符限制")
    if len(subject) < 10:
        warnings.append("主题描述过于简略")
    
    # 规则4: 检查类型与修改文件是否匹配
    file_changes = get_changed_files()
    commit_type = extract_type(commit_msg)
    if not validate_type_files_match(commit_type, file_changes):
        warnings.append(f"提交类型 '{commit_type}' 与修改文件类型可能不匹配")
    
    return CheckResult(errors=errors, warnings=warnings)
```

### 2.2 提交频率分析

#### 2.2.1 正常提交模式基线

| 角色 | 工作日提交频率 | 单次提交文件数 | 提交时间分布 |
|-----|--------------|---------------|-------------|
| 韩信(研发) | 3-8 次/天 | 1-10 个文件 | 09:00-19:00 |
| 张良(产品) | 1-3 次/天 | 1-5 个文件 | 09:00-18:00 |
| 萧何(架构) | 1-2 次/天 | 1-3 个文件 | 10:00-17:00 |
| 周勃(运维) | 1-5 次/天 | 1-20 个文件 | 全天(含值班) |
| 陆贾(知识库) | 2-4 次/天 | 1-10 个文件 | 09:00-18:00 |
| 陈平(测试) | 1-3 次/天 | 1-5 个文件 | 10:00-18:00 |

#### 2.2.2 异常提交模式检测

```python
# 伪代码：异常提交检测
def detect_anomalous_commits(commits: List[Commit], window: str = "7d") -> List[Alert]:
    alerts = []
    
    # 检测1: 批量提交（可能遗漏分解）
    for commit in commits:
        if commit.file_count > 20:
            alerts.append(Alert(
                level="warning",
                message=f"大量文件修改: {commit.file_count} 个文件",
                commit=commit.hash,
                suggestion="建议分解为多个小提交"
            ))
    
    # 检测2: 深夜提交（可能非工作时间）
    for commit in commits:
        hour = commit.timestamp.hour
        if hour < 7 or hour > 23:
            alerts.append(Alert(
                level="info",
                message=f"非工作时间提交: {commit.timestamp}",
                commit=commit.hash,
                suggestion="确认是否为计划内值班或紧急修复"
            ))
    
    # 检测3: 提交频率异常
    author_commits = group_by_author(commits)
    for author, author_commit_list in author_commits.items():
        hourly_rate = len(author_commit_list) / 24
        if hourly_rate > 2:  # 每小时超过2次
            alerts.append(Alert(
                level="warning",
                message=f"{author} 提交频率异常高: {hourly_rate:.1f} 次/小时",
                suggestion="检查是否存在自动化脚本或频繁小提交"
            ))
    
    # 检测4: 空提交或重复提交
    for commit in commits:
        if commit.is_empty:
            alerts.append(Alert(
                level="error",
                message="空提交 detected",
                commit=commit.hash
            ))
    
    return alerts
```

### 2.3 代码改动量统计

#### 2.3.1 按角色统计

```python
# 伪代码：角色维度改动统计
def generate_role_contribution_report(start_date: str, end_date: str) -> Report:
    report = {
        "period": f"{start_date} to {end_date}",
        "by_role": {},
        "by_type": {}
    }
    
    # 角色映射配置（从 commit author 或 metadata 识别）
    role_mapping = {
        "hanxin": "研发工程师",
        "zhangliang": "产品经理", 
        "xiaohe": "架构师",
        "zhoubo": "运维工程师",
        "lujia": "知识库管理员",
        "chenping": "测试工程师",
        "caocan": "PMO",
        "shusuntong": "设计师",
        "xiahouying": "私人助理",
        "lishiyi": "外部助理"
    }
    
    commits = get_commits_in_range(start_date, end_date)
    
    for commit in commits:
        role = role_mapping.get(commit.author, "其他")
        stats = calculate_diff_stats(commit)
        
        if role not in report["by_role"]:
            report["by_role"][role] = {
                "commits": 0,
                "files_changed": 0,
                "insertions": 0,
                "deletions": 0,
                "net_change": 0
            }
        
        report["by_role"][role]["commits"] += 1
        report["by_role"][role]["files_changed"] += stats.files
        report["by_role"][role]["insertions"] += stats.insertions
        report["by_role"][role]["deletions"] += stats.deletions
        report["by_role"][role]["net_change"] += (stats.insertions - stats.deletions)
    
    return report
```

#### 2.3.2 按改动类型统计

| 改动类型 | 识别规则 | 健康阈值 |
|---------|---------|---------|
| 功能代码 | `feat:` 提交，修改 src/ | 新增代码需有对应测试 |
| Bug 修复 | `fix:` 提交 | 平均每周 < 5% 代码行数 |
| 文档更新 | `docs:` 提交，修改 *.md | 与功能改动比例 ≥ 1:3 |
| 重构 | `refactor:` 提交 | 单次重构 < 500 行 |
| 配置变更 | `chore:` 提交，修改 configs/ | 需有变更说明 |

### 2.4 分支策略合规检查

#### 2.4.1 分支模型

```
main (保护分支)
  ├── develop (日常开发)
  │     ├── feature/story-XXX (功能分支)
  │     ├── feature/story-YYY
  │     └── hotfix/bug-XXX (热修复)
  └── release/vX.Y.Z (发布分支)
```

#### 2.4.2 分支合规检查项

```python
# 伪代码：分支策略检查
def check_branch_compliance(repo_path: str) -> ComplianceReport:
    report = ComplianceReport()
    
    # 检查1: main 分支保护
    main_protection = check_branch_protection("main")
    if not main_protection.enabled:
        report.add_violation("main", "分支未启用保护规则")
    if not main_protection.require_reviews:
        report.add_warning("main", "建议强制 Code Review")
    
    # 检查2: 分支命名规范
    valid_patterns = [
        r'^main$',
        r'^develop$',
        r'^feature/[a-z0-9-]+$',
        r'^hotfix/[a-z0-9-]+$',
        r'^release/v\d+\.\d+\.\d+$'
    ]
    
    for branch in list_branches():
        if not any(re.match(p, branch) for p in valid_patterns):
            report.add_violation(branch, "分支命名不符合规范")
    
    # 检查3: 过期分支清理
    stale_branches = get_branches_inactive_for(days=30)
    for branch in stale_branches:
        if not branch.startswith("release/"):
            report.add_warning(branch, "分支超过30天无活动，建议清理")
    
    # 检查4: 合并策略
    for commit in get_merge_commits(since="7d"):
        if commit.is_squash_merge:
            report.add_info(commit.branch, "使用 squash merge，符合规范")
        elif commit.has_clean_history:
            report.add_info(commit.branch, "提交历史清晰")
        else:
            report.add_warning(commit.branch, "建议整理提交历史")
    
    return report
```

---

## 3. 文档更新校验策略

### 3.1 文档修改时间戳检查

#### 3.1.1 关键文档清单

| 文档类别 | 路径模式 | 修改监控级别 |
|---------|---------|-------------|
| 角色身份 | `agents/*/IDENTITY.md` | 高 - 任何修改需记录 |
| 流程文档 | `workflows/*.md` | 高 - 修改需通知全员 |
| 看板配置 | `notion/*.md` | 高 - 需同步 Notion |
| 技能文档 | `skills/**/README.md` | 中 - 技能更新需记录 |
| 治理规则 | `governance/*.md` | 高 - 规则变更需审批 |
| 项目级文档 | `*.md` (根目录) | 高 - 项目核心文档 |
| Agent 配置 | `agents/*/*.md` | 中 - 角色专属配置 |

#### 3.1.2 时间戳检查逻辑

```python
# 伪代码：文档修改时间戳检查
def check_document_timestamps() -> TimestampReport:
    report = TimestampReport()
    
    # 检查1: 文档修改时间与 Git 提交时间一致性
    for doc_path in get_tracked_documents():
        file_mtime = os.path.getmtime(doc_path)
        git_mtime = get_last_git_commit_time(doc_path)
        
        time_diff = abs(file_mtime - git_mtime)
        if time_diff > 60:  # 超过60秒差异
            report.add_discrepancy(
                doc_path,
                file_mtime,
                git_mtime,
                f"文件修改时间与 Git 提交时间不一致，差异 {time_diff} 秒"
            )
    
    # 检查2: 检查文档最后更新时间是否过期
    for doc_path in get_critical_documents():
        last_update = get_last_update_time(doc_path)
        days_since_update = (now() - last_update).days
        
        if days_since_update > 90:
            report.add_warning(doc_path, f"文档超过90天未更新，建议审查")
        elif days_since_update > 30:
            report.add_info(doc_path, f"文档 {days_since_update} 天前更新")
    
    # 检查3: 检查元数据中的最后更新日期
    for doc_path in get_markdown_documents():
        metadata_date = extract_metadata_date(doc_path)
        if metadata_date:
            actual_date = get_last_update_time(doc_path).date()
            if metadata_date != actual_date:
                report.add_warning(
                    doc_path,
                    f"元数据最后更新日期 ({metadata_date}) 与实际不符 ({actual_date})"
                )
    
    return report
```

### 3.2 文档版本与 Git 提交关联

#### 3.2.1 版本追踪机制

每个关键文档应在头部包含版本元数据：

```markdown
---
title: 文档标题
version: 1.2.3
last_updated: 2026-03-27
last_updated_by: zhangliang
related_commits:
  - abc1234  # 初始版本
  - def5678  # 重大修订
---
```

#### 3.2.2 关联检查逻辑

```python
# 伪代码：文档版本与 Git 关联检查
def verify_document_git_association() -> AssociationReport:
    report = AssociationReport()
    
    for doc_path in get_versioned_documents():
        metadata = extract_frontmatter(doc_path)
        
        # 检查1: 版本号格式
        if "version" in metadata:
            if not is_semver(metadata["version"]):
                report.add_error(doc_path, "版本号不符合 SemVer 规范")
        else:
            report.add_warning(doc_path, "缺少版本号元数据")
        
        # 检查2: 最后更新时间与 Git 提交关联
        if "last_updated" in metadata:
            git_commits = get_commits_touching_file(doc_path, since=metadata["last_updated"])
            if not git_commits:
                report.add_warning(doc_path, "元数据最后更新时间与 Git 提交记录不匹配")
        
        # 检查3: 关联提交哈希有效性
        if "related_commits" in metadata:
            for commit_hash in metadata["related_commits"]:
                if not is_valid_commit_hash(commit_hash):
                    report.add_error(doc_path, f"无效的关联提交哈希: {commit_hash}")
                elif not commit_touches_file(commit_hash, doc_path):
                    report.add_warning(doc_path, f"提交 {commit_hash} 未修改此文件")
    
    return report
```

### 3.3 文档审批流程验证

#### 3.3.1 审批级别定义

| 审批级别 | 适用文档 | 审批人 | 留痕要求 |
|---------|---------|-------|---------|
| L1-通知 | 日常更新、小修正 | 无需审批 | Git 提交记录 |
| L2-审查 | 流程变更、角色调整 | 同级角色 Review | PR + Review 记录 |
| L3-审批 | 治理规则、架构变更 | 对应负责人 | 审批记录 + 会议纪要 |
| L4-决策 | 重大变更、方向调整 | Owner(刘邦) | 决策记录 + 全员通知 |

#### 3.3.2 审批流程检查

```python
# 伪代码：审批流程检查
def check_document_approval_workflow(doc_path: str) -> ApprovalCheck:
    result = ApprovalCheck()
    
    # 根据文档路径确定所需审批级别
    approval_level = determine_required_approval_level(doc_path)
    result.required_level = approval_level
    
    # 获取 Git 提交信息
    commits = get_commits_touching_file(doc_path, limit=5)
    
    if approval_level >= L2:
        # 检查是否通过 PR 合并
        if not is_merged_via_pr(commits[0]):
            result.add_violation("L2+ 变更必须通过 PR 合并")
        
        # 检查是否有 Review 记录
        reviews = get_pr_reviews(commits[0])
        if not reviews or len([r for r in reviews if r.approved]) == 0:
            result.add_violation("L2+ 变更必须至少一个 Approval")
    
    if approval_level >= L3:
        # 检查是否有关联的 Notion 审批记录
        notion_record = find_notion_approval_record(doc_path)
        if not notion_record:
            result.add_violation("L3+ 变更必须有 Notion 审批记录")
        elif notion_record.status != "已批准":
            result.add_violation(f"审批状态为: {notion_record.status}")
    
    if approval_level >= L4:
        # 检查是否有 Owner 决策记录
        decision_record = find_owner_decision(doc_path)
        if not decision_record:
            result.add_violation("L4 变更必须有 Owner 决策记录")
    
    return result
```

### 3.4 文档模板合规检查

#### 3.4.1 模板检查规则

```python
# 伪代码：文档模板合规检查
TEMPLATE_RULES = {
    "agents/*/IDENTITY.md": {
        "required_sections": ["模型配置"],
        "required_frontmatter": ["name", "description"],
        "max_length": 2000,
        "required_keywords": ["官方职位", "核心权责", "汇报关系"]
    },
    "workflows/*.md": {
        "required_sections": ["流程概述", "执行步骤"],
        "required_frontmatter": ["文档版本", "生效日期"],
        "must_have_diagram": True,
        "required_keywords": ["负责人", "输入", "输出", "验收标准"]
    },
    "notion/*.md": {
        "required_sections": ["字段定义"],
        "required_frontmatter": [],
        "must_have_table": True
    },
    "skills/**/*.md": {
        "required_sections": ["安装", "使用"],
        "required_frontmatter": ["version"],
        "must_have_code_block": True
    }
}

def check_document_template_compliance(doc_path: str) -> TemplateReport:
    report = TemplateReport()
    content = read_file(doc_path)
    
    # 匹配适用的模板规则
    rules = None
    for pattern, rule_set in TEMPLATE_RULES.items():
        if fnmatch(doc_path, pattern):
            rules = rule_set
            break
    
    if not rules:
        return report  # 无特定模板要求
    
    # 检查必需章节
    if "required_sections" in rules:
        for section in rules["required_sections"]:
            if not has_section(content, section):
                report.add_violation(f"缺少必需章节: {section}")
    
    # 检查 Frontmatter
    if "required_frontmatter" in rules:
        frontmatter = extract_frontmatter(content)
        for key in rules["required_frontmatter"]:
            if key not in frontmatter:
                report.add_violation(f"缺少 Frontmatter 字段: {key}")
    
    # 检查图表
    if rules.get("must_have_diagram"):
        if not has_mermaid_diagram(content) and not has_flowchart(content):
            report.add_warning("建议添加流程图")
    
    # 检查关键词
    if "required_keywords" in rules:
        for keyword in rules["required_keywords"]:
            if keyword not in content:
                report.add_violation(f"缺少关键内容: {keyword}")
    
    return report
```

---

## 4. Notion 看板校验策略

### 4.1 外部需求登记完整性检查

#### 4.1.1 必填字段检查

```python
# 伪代码：外部需求完整性检查
EXTERNAL_REQ_REQUIRED_FIELDS = [
    "需求标题",      # title
    "需求描述",      # rich_text
    "来源渠道",      # select
    "优先级",        # select
    "状态"           # status
]

EXTERNAL_REQ_SOURCE_OPTIONS = [
    "客户反馈",
    "市场调研",
    "竞品分析",
    "内部建议",
    "其他"
]

def check_external_requirement_completeness(notion_client) -> CompletenessReport:
    report = CompletenessReport()
    
    # 获取外部需求看板中的所有记录
    external_reqs = notion_client.query_database(
        database_id=EXTERNAL_REQ_DB_ID
    )
    
    for req in external_reqs:
        req_id = req["id"]
        req_title = get_title(req)
        
        # 检查必填字段
        for field in EXTERNAL_REQ_REQUIRED_FIELDS:
            if not has_value(req, field):
                report.add_violation(req_id, f"[{req_title}] 缺少必填字段: {field}")
        
        # 检查来源渠道有效性
        source = get_select_value(req, "来源渠道")
        if source and source not in EXTERNAL_REQ_SOURCE_OPTIONS:
            report.add_warning(req_id, f"[{req_title}] 未知来源渠道: {source}")
        
        # 检查已采纳需求是否关联 Story
        status = get_status_value(req, "状态")
        if status == "已采纳":
            related_story = get_relation_value(req, "关联需求")
            if not related_story:
                report.add_violation(
                    req_id, 
                    f"[{req_title}] 已采纳但未关联 Story"
                )
        
        # 检查时间合理性
        created_time = req["created_time"]
        if is_future_date(created_time):
            report.add_error(req_id, f"[{req_title}] 创建时间异常: 未来日期")
    
    return report
```

#### 4.1.2 外部需求流转时效检查

```python
# 伪代码：外部需求时效检查
EXTERNAL_REQ_SLA = {
    "待评估": timedelta(hours=24),      # 24小时内完成评估
    "已评估": timedelta(hours=48),      # 48小时内完成决策
    "已采纳": timedelta(hours=4)        # 采纳后4小时内创建 Story
}

def check_external_requirement_timeliness(notion_client) -> TimelinessReport:
    report = TimelinessReport()
    
    external_reqs = notion_client.query_database(EXTERNAL_REQ_DB_ID)
    
    for req in external_reqs:
        status = get_status_value(req, "状态")
        status_history = get_status_change_history(req)
        
        if status in EXTERNAL_REQ_SLA:
            # 获取进入当前状态的时间
            entered_time = status_history.get(status, req["created_time"])
            time_in_status = now() - entered_time
            sla = EXTERNAL_REQ_SLA[status]
            
            if time_in_status > sla:
                report.add_violation(
                    req["id"],
                    f"状态 '{status}' 已持续 {time_in_status.total_hours():.1f} 小时，"
                    f"超过 SLA ({sla.total_hours():.0f} 小时)"
                )
            elif time_in_status > sla * 0.8:
                report.add_warning(
                    req["id"],
                    f"状态 '{status}' 即将超时，已持续 {time_in_status.total_hours():.1f} 小时"
                )
    
    return report
```

### 4.2 Story/Task 创建规范性检查

#### 4.2.1 Story 规范检查

```python
# 伪代码：Story 规范检查
STORY_REQUIRED_FIELDS = [
    "Story 标题",
    "详细描述",
    "状态",
    "优先级"
]

STORY_VALID_TRANSITIONS = {
    "待开发": ["开发中", "已取消"],
    "开发中": ["测试中", "已取消"],
    "测试中": ["已完成", "开发中"],
    "已完成": [],
    "已取消": []
}

def check_story_compliance(notion_client) -> StoryReport:
    report = StoryReport()
    
    stories = notion_client.query_database(STORY_DB_ID)
    
    for story in stories:
        story_id = story["id"]
        
        # 检查必填字段
        for field in STORY_REQUIRED_FIELDS:
            if not has_value(story, field):
                report.add_violation(story_id, f"缺少必填字段: {field}")
        
        # 检查标题格式
        title = get_title(story)
        if not re.match(r'\[[\w-]+\] .+', title):
            report.add_warning(story_id, "标题格式建议: [模块] 描述")
        
        # 检查状态流转合规性
        status_history = get_property_history(story, "状态")
        for i in range(1, len(status_history)):
            prev_status = status_history[i-1]["value"]
            curr_status = status_history[i]["value"]
            
            if curr_status not in STORY_VALID_TRANSITIONS.get(prev_status, []):
                report.add_violation(
                    story_id,
                    f"非法状态流转: {prev_status} → {curr_status}"
                )
        
        # 检查任务拆分
        task_count = get_rollup_value(story, "Task 数量")
        if status in ["开发中", "测试中", "已完成"] and task_count == 0:
            report.add_warning(story_id, "进行中/已完成 Story 没有关联 Task")
        
        # 检查迭代关联
        if status != "待开发":
            iteration = get_relation_value(story, "所属迭代")
            if not iteration:
                report.add_violation(story_id, "非待开发状态必须关联迭代")
    
    return report
```

#### 4.2.2 Task 规范检查

```python
# 伪代码：Task 规范检查
TASK_REQUIRED_FIELDS = [
    "Task 标题",
    "状态",
    "所属 Story",
    "任务类型"
]

TASK_TYPE_OPTIONS = ["设计", "开发", "测试", "文档", "调研", "评审", "其他"]

def check_task_compliance(notion_client) -> TaskReport:
    report = TaskReport()
    
    tasks = notion_client.query_database(TASK_DB_ID)
    
    for task in tasks:
        task_id = task["id"]
        
        # 检查必填字段
        for field in TASK_REQUIRED_FIELDS:
            if not has_value(task, field):
                report.add_violation(task_id, f"缺少必填字段: {field}")
        
        # 检查任务类型有效性
        task_type = get_select_value(task, "任务类型")
        if task_type and task_type not in TASK_TYPE_OPTIONS:
            report.add_warning(task_id, f"未知任务类型: {task_type}")
        
        # 检查时间记录完整性
        status = get_status_value(task, "状态")
        if status == "进行中":
            if not has_value(task, "开始时间"):
                report.add_warning(task_id, "进行中 Task 建议记录开始时间")
        
        if status == "已完成":
            if not has_value(task, "结束时间"):
                report.add_violation(task_id, "已完成 Task 必须记录结束时间")
            if not has_value(task, "实际工时"):
                report.add_warning(task_id, "已完成 Task 建议记录实际工时")
        
        # 检查关联关系
        story = get_relation_value(task, "所属 Story")
        if story:
            story_status = get_story_status(story)
            if story_status == "已取消" and status != "已取消":
                report.add_warning(task_id, "所属 Story 已取消，建议同步取消")
    
    return report
```

### 4.3 状态流转合规性检查

```python
# 伪代码：状态流转合规性检查
STATE_TRANSITION_RULES = {
    "Task": {
        "待处理": ["进行中", "已阻塞", "已取消"],
        "进行中": ["已完成", "已阻塞", "已取消"],
        "已阻塞": ["进行中", "已取消"],
        "已完成": [],
        "已取消": []
    },
    "Bug": {
        "新增": ["修复中", "非 Bug", "需求设计问题"],
        "修复中": ["已修复"],
        "已修复": ["已验证", "重复打开"],
        "重复打开": ["修复中"],
        "非 Bug": [],
        "需求设计问题": [],
        "已验证": []
    },
    "Story": {
        "待开发": ["开发中", "已取消"],
        "开发中": ["测试中", "已取消"],
        "测试中": ["已完成", "开发中"],
        "已完成": [],
        "已取消": []
    }
}

def check_state_transition_compliance(notion_client) -> TransitionReport:
    report = TransitionReport()
    
    for entity_type, rules in STATE_TRANSITION_RULES.items():
        db_id = get_database_id(entity_type)
        items = notion_client.query_database(db_id)
        
        for item in items:
            item_id = item["id"]
            history = get_status_change_history(item)
            
            for i in range(1, len(history)):
                prev = history[i-1]["value"]
                curr = history[i]["value"]
                timestamp = history[i]["timestamp"]
                
                # 检查流转是否合法
                if curr not in rules.get(prev, []):
                    report.add_violation(
                        item_id,
                        f"非法状态流转: {prev} → {curr} at {timestamp}"
                    )
                
                # 检查流转责任人
                actor = history[i].get("actor")
                if not actor:
                    report.add_warning(item_id, f"状态变更 {prev}→{curr} 缺少操作人记录")
    
    return report
```

### 4.4 Bug 记录完整性检查

```python
# 伪代码：Bug 记录完整性检查
BUG_REQUIRED_FIELDS = [
    "Bug 标题",
    "详细描述",
    "状态",
    "严重程度",
    "优先级"
]

BUG_SEVERITY_OPTIONS = ["致命", "严重", "一般", "轻微", "建议"]
BUG_PRIORITY_OPTIONS = ["P0-立即修复", "P1-高优先级", "P2-普通", "P3-低优先级"]

def check_bug_record_completeness(notion_client) -> BugReport:
    report = BugReport()
    
    bugs = notion_client.query_database(BUG_DB_ID)
    
    for bug in bugs:
        bug_id = bug["id"]
        status = get_status_value(bug, "状态")
        
        # 检查必填字段
        for field in BUG_REQUIRED_FIELDS:
            if not has_value(bug, field):
                report.add_violation(bug_id, f"缺少必填字段: {field}")
        
        # 检查严重程度与优先级匹配
        severity = get_select_value(bug, "严重程度")
        priority = get_select_value(bug, "优先级")
        
        if severity == "致命" and priority != "P0-立即修复":
            report.add_warning(bug_id, "致命 Bug 建议使用 P0 优先级")
        
        # 检查已修复 Bug 的必填信息
        if status in ["已修复", "已验证"]:
            if not has_value(bug, "修复时间"):
                report.add_violation(bug_id, "已修复 Bug 必须记录修复时间")
            if not has_value(bug, "修复说明"):
                report.add_warning(bug_id, "建议填写修复说明")
            if not has_value(bug, "负责人"):
                report.add_violation(bug_id, "已修复 Bug 必须记录修复负责人")
        
        if status == "已验证":
            if not has_value(bug, "验证人"):
                report.add_warning(bug_id, "已验证 Bug 建议记录验证人")
        
        # 检查关联关系
        if status != "非 Bug":
            related_task = get_relation_value(bug, "关联 Task")
            related_story = get_relation_value(bug, "关联 Story")
            if not related_task and not related_story:
                report.add_warning(bug_id, "Bug 建议关联到 Task 或 Story")
    
    return report
```

### 4.5 每日复盘及时性检查

```python
# 伪代码：每日复盘及时性检查
def check_retrospective_timeliness(notion_client) -> RetroReport:
    report = RetroReport()
    
    # 获取所有复盘记录
    retrospectives = notion_client.query_database(RETRO_DB_ID)
    
    # 检查复盘是否每日进行
    today = date.today()
    expected_retro_dates = get_expected_retro_dates(last_n_days=30)
    actual_retro_dates = set()
    
    for retro in retrospectives:
        retro_date = get_date_value(retro, "复盘日期(日期)")
        if retro_date:
            actual_retro_dates.add(retro_date)
            
            # 检查复盘状态
            status = get_status_value(retro, "复盘状态")
            if status == "进行中":
                # 检查是否超时（复盘应在当天完成）
                if retro_date < today:
                    report.add_warning(
                        retro["id"],
                        f"{retro_date} 复盘未完成，当前状态: {status}"
                    )
            
            # 检查复盘内容完整性
            if status == "已完成":
                if not has_value(retro, "当日产出"):
                    report.add_violation(retro["id"], "已完成复盘缺少当日产出")
                
                # 检查关联迭代
                iteration = get_relation_value(retro, "关联迭代")
                if not iteration:
                    report.add_warning(retro["id"], "复盘建议关联到对应迭代")
    
    # 检查缺失的复盘
    for expected_date in expected_retro_dates:
        if expected_date not in actual_retro_dates:
            # 跳过周末
            if expected_date.weekday() >= 5:
                continue
            report.add_violation(
                "N/A",
                f"缺少 {expected_date} 的复盘记录"
            )
    
    return report
```

---

## 5. 复盘同步校验策略

### 5.1 复盘记录与 Task/Bug 的关联性

```python
# 伪代码：复盘关联性检查
def check_retrospective_task_bug_association(notion_client) -> AssociationReport:
    report = AssociationReport()
    
    retrospectives = notion_client.query_database(RETRO_DB_ID)
    
    for retro in retrospectives:
        retro_id = retro["id"]
        retro_date = get_date_value(retro, "复盘日期(日期)")
        
        if not retro_date:
            continue
        
        # 获取当日产出的文本内容
        output = get_rich_text_value(retro, "当日产出")
        
        # 从产出文本中提取提及的 Task/Bug ID
        mentioned_tasks = extract_task_ids(output)
        mentioned_bugs = extract_bug_ids(output)
        
        # 获取当日实际完成的 Task/Bug
        actual_completed_tasks = get_completed_tasks_on_date(retro_date)
        actual_completed_bugs = get_completed_bugs_on_date(retro_date)
        
        # 检查覆盖度
        task_coverage = len(set(mentioned_tasks) & set(actual_completed_tasks))
        bug_coverage = len(set(mentioned_bugs) & set(actual_completed_bugs))
        
        if len(actual_completed_tasks) > 0:
            coverage_rate = task_coverage / len(actual_completed_tasks)
            if coverage_rate < 0.8:
                report.add_warning(
                    retro_id,
                    f"Task 覆盖度 {coverage_rate*100:.0f}% 偏低，"
                    f"当日完成 {len(actual_completed_tasks)} 个，复盘提及 {task_coverage} 个"
                )
        
        # 检查阻塞问题是否有对应 Task/Bug
        blockers = get_rich_text_value(retro, "阻塞问题")
        if blockers:
            blocker_tasks = extract_task_ids(blockers)
            for task_id in blocker_tasks:
                task = notion_client.get_page(task_id)
                if task and get_status_value(task, "状态") != "已阻塞":
                    report.add_warning(
                        retro_id,
                        f"复盘提及的阻塞 Task {task_id} 当前状态非'已阻塞'"
                    )
    
    return report
```

### 5.2 复盘改进项的跟进状态

```python
# 伪代码：改进项跟进状态检查
def check_improvement_items_followup(notion_client) -> FollowupReport:
    report = FollowupReport()
    
    # 获取所有改进项
    all_retros = notion_client.query_database(RETRO_DB_ID)
    improvement_items = []
    
    for retro in all_retros:
        retro_date = get_date_value(retro, "复盘日期(日期)")
        improvements_text = get_rich_text_value(retro, "改进项")
        
        if improvements_text:
            items = parse_improvement_items(improvements_text)
            for item in items:
                improvement_items.append({
                    "retro_id": retro["id"],
                    "retro_date": retro_date,
                    "item": item["description"],
                    "owner": item.get("owner"),
                    "deadline": item.get("deadline"),
                    "status": item.get("status", "待处理")
                })
    
    # 检查每个改进项的跟进状态
    for item in improvement_items:
        # 检查是否超时
        if item["deadline"] and item["deadline"] < date.today():
            if item["status"] not in ["已完成", "已放弃"]:
                report.add_violation(
                    item["retro_id"],
                    f"改进项超期: {item['item'][:50]}..."
                )
        
        # 检查责任人
        if not item["owner"]:
            report.add_warning(
                item["retro_id"],
                f"改进项未指定负责人: {item['item'][:50]}..."
            )
        
        # 检查30天内的改进项完成情况
        if item["retro_date"] and (date.today() - item["retro_date"]).days <= 30:
            if item["status"] == "待处理":
                report.add_info(
                    item["retro_id"],
                    f"改进项待跟进: {item['item'][:50]}..."
                )
    
    # 统计改进项闭环率
    total_items = len(improvement_items)
    completed_items = len([i for i in improvement_items if i["status"] == "已完成"])
    closed_rate = completed_items / total_items if total_items > 0 else 0
    
    report.summary["total_improvements"] = total_items
    report.summary["completed_improvements"] = completed_items
    report.summary["closure_rate"] = f"{closed_rate*100:.1f}%"
    
    return report
```

### 5.3 复盘 Token 开销记录

```python
# 伪代码：Token 开销记录检查
def check_retrospective_token_recording(notion_client) -> TokenReport:
    report = TokenReport()
    
    retrospectives = notion_client.query_database(RETRO_DB_ID)
    
    for retro in retrospectives:
        retro_id = retro["id"]
        retro_date = get_date_value(retro, "复盘日期(日期)")
        
        # 获取关联迭代
        iteration = get_relation_value(retro, "关联迭代")
        if iteration:
            # 获取迭代的 Token 开销
            iteration_token = get_number_value(iteration, "Token 开销总计")
            
            # 获取当日所有 Task 的 Token 总和
            tasks = get_tasks_in_iteration(iteration)
            tasks_on_date = [t for t in tasks if get_date_value(t, "结束时间") == retro_date]
            task_tokens = sum(get_number_value(t, "Token 开销") or 0 for t in tasks_on_date)
            
            # 对比检查
            if iteration_token and abs(iteration_token - task_tokens) > iteration_token * 0.1:
                report.add_warning(
                    retro_id,
                    f"Token 开销差异: 迭代总计 {iteration_token}, "
                    f"当日 Task 合计 {task_tokens}"
                )
        
        # 检查复盘本身的资源消耗记录（如果有）
        # 这部分可以根据实际情况扩展
    
    return report
```

### 5.4 复盘周期合规性检查

```python
# 伪代码：复盘周期合规性检查
def check_retrospective_cycle_compliance(notion_client) -> CycleReport:
    report = CycleReport()
    
    # 定义工作日（排除周末）
    def is_workday(d: date) -> bool:
        return d.weekday() < 5
    
    # 获取最近30个工作日
    end_date = date.today()
    start_date = end_date - timedelta(days=45)
    
    expected_retro_days = [
        d for d in daterange(start_date, end_date)
        if is_workday(d)
    ]
    
    # 获取实际有复盘的日期
    retrospectives = notion_client.query_database(RETRO_DB_ID)
    actual_retro_days = set()
    
    for retro in retrospectives:
        retro_date = get_date_value(retro, "复盘日期(日期)")
        if retro_date and start_date <= retro_date <= end_date:
            actual_retro_days.add(retro_date)
    
    # 计算合规率
    missed_days = [d for d in expected_retro_days if d not in actual_retro_days]
    compliance_rate = (len(expected_retro_days) - len(missed_days)) / len(expected_retro_days)
    
    report.summary["expected_days"] = len(expected_retro_days)
    report.summary["actual_days"] = len(actual_retro_days)
    report.summary["missed_days"] = len(missed_days)
    report.summary["compliance_rate"] = f"{compliance_rate*100:.1f}%"
    
    # 记录缺失的复盘
    for missed_day in missed_days:
        report.add_violation(
            "N/A",
            f"缺少 {missed_day} ({missed_day.strftime('%A')}) 的复盘记录"
        )
    
    # 检查复盘时间分布
    for retro in retrospectives:
        retro_date = get_date_value(retro, "复盘日期(日期)")
        created_time = retro["created_time"]
        
        if retro_date:
            # 复盘应在当天或次日创建
            created_date = datetime.fromisoformat(created_time).date()
            day_diff = (created_date - retro_date).days
            
            if day_diff > 1:
                report.add_warning(
                    retro["id"],
                    f"复盘记录延迟 {day_diff} 天创建"
                )
            elif day_diff < 0:
                report.add_error(
                    retro["id"],
                    f"复盘记录创建于复盘日期之前，时间异常"
                )
    
    return report
```

---

## 6. 校验脚本设计

### 6.1 脚本架构说明

```
scripts/traceability/
├── README.md                    # 使用说明
├── requirements.txt             # Python 依赖
├── config.yaml                  # 校验配置
├── main.py                      # 主入口
├── core/                        # 核心模块
│   ├── __init__.py
│   ├── git_checker.py           # Git 校验
│   ├── document_checker.py      # 文档校验
│   ├── notion_checker.py        # Notion 校验
│   ├── retro_checker.py         # 复盘校验
│   └── reporter.py              # 报告生成
├── utils/                       # 工具模块
│   ├── __init__.py
│   ├── notion_client.py         # Notion API 封装
│   ├── git_helper.py            # Git 操作封装
│   └── logger.py                # 日志工具
└── reports/                     # 报告输出目录
    ├── daily/                   # 日报
    ├── weekly/                  # 周报
    └── iteration/               # 迭代报告
```

### 6.2 各校验模块逻辑伪代码

#### 6.2.1 Git 校验模块 (git_checker.py)

```python
"""
Git 提交校验模块
"""

import re
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta

@dataclass
class CommitInfo:
    hash: str
    author: str
    email: str
    timestamp: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int

@dataclass
class GitCheckResult:
    errors: List[str]
    warnings: List[str]
    info: List[str]
    stats: Dict

class GitCommitChecker:
    """Git 提交规范检查器"""
    
    # Conventional Commits 类型
    VALID_TYPES = [
        'feat', 'fix', 'docs', 'style', 'refactor',
        'test', 'chore', 'design', 'workflow', 'agent'
    ]
    
    # 提交信息正则
    COMMIT_PATTERN = re.compile(
        r'^(feat|fix|docs|style|refactor|test|chore|design|workflow|agent)'
        r'(?:\([\w\-/]+\))?!?: .+'
    )
    
    # 角色映射
    ROLE_MAPPING = {
        'hanxin': '研发工程师',
        'zhangliang': '产品经理',
        'xiaohe': '架构师',
        'zhoubo': '运维工程师',
        'lujia': '知识库管理员',
        'chenping': '测试工程师',
        'caocan': 'PMO',
        'shusuntong': '设计师',
        'xiahouying': '私人助理',
        'lishiyi': '外部助理'
    }
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def run_all_checks(self, since: str = "7 days ago") -> GitCheckResult:
        """运行所有 Git 检查"""
        result = GitCheckResult([], [], [], {})
        
        commits = self.get_commits(since)
        
        # 1. 提交信息规范检查
        msg_result = self.check_commit_messages(commits)
        result.errors.extend(msg_result.errors)
        result.warnings.extend(msg_result.warnings)
        
        # 2. 提交频率分析
        freq_result = self.analyze_commit_frequency(commits)
        result.warnings.extend(freq_result.warnings)
        result.info.extend(freq_result.info)
        
        # 3. 改动量统计
        result.stats = self.calculate_contribution_stats(commits)
        
        # 4. 分支策略检查
        branch_result = self.check_branch_compliance()
        result.errors.extend(branch_result.errors)
        result.warnings.extend(branch_result.warnings)
        
        return result
    
    def get_commits(self, since: str) -> List[CommitInfo]:
        """获取指定时间范围内的提交"""
        cmd = [
            'git', 'log', f'--since={since}',
            '--pretty=format:%H|%an|%ae|%at|%s',
            '--shortstat'
        ]
        output = subprocess.check_output(cmd, cwd=self.repo_path).decode('utf-8')
        return self._parse_git_log(output)
    
    def _parse_git_log(self, log_output: str) -> List[CommitInfo]:
        """解析 Git 日志输出"""
        commits = []
        lines = log_output.strip().split('\n')
        
        i = 0
        while i < len(lines):
            if '|' in lines[i]:
                parts = lines[i].split('|')
                commit_hash = parts[0]
                author = parts[1]
                email = parts[2]
                timestamp = datetime.fromtimestamp(int(parts[3]))
                message = parts[4]
                
                # 解析统计行
                files_changed = 0
                insertions = 0
                deletions = 0
                
                if i + 1 < len(lines) and 'changed' in lines[i + 1]:
                    stat_line = lines[i + 1]
                    # 解析类似 "3 files changed, 50 insertions(+), 10 deletions(-)"
                    files_match = re.search(r'(\d+) file', stat_line)
                    if files_match:
                        files_changed = int(files_match.group(1))
                    
                    insert_match = re.search(r'(\d+) insertion', stat_line)
                    if insert_match:
                        insertions = int(insert_match.group(1))
                    
                    delete_match = re.search(r'(\d+) deletion', stat_line)
                    if delete_match:
                        deletions = int(delete_match.group(1))
                    
                    i += 1
                
                commits.append(CommitInfo(
                    hash=commit_hash,
                    author=author,
                    email=email,
                    timestamp=timestamp,
                    message=message,
                    files_changed=files_changed,
                    insertions=insertions,
                    deletions=deletions
                ))
            i += 1
        
        return commits
    
    def check_commit_messages(self, commits: List[CommitInfo]) -> GitCheckResult:
        """检查提交信息规范"""
        result = GitCheckResult([], [], [], {})
        
        for commit in commits:
            # 检查格式
            if not self.COMMIT_PATTERN.match(commit.message):
                result.errors.append(
                    f"[{commit.hash[:7]}] 提交信息格式不符合 Conventional Commits: {commit.message[:50]}"
                )
            
            # 检查主题长度
            subject = commit.message.split('\n')[0]
            if len(subject) > 72:
                result.warnings.append(
                    f"[{commit.hash[:7]}] 提交主题过长 ({len(subject)} 字符): {subject[:50]}..."
                )
            
            # 检查是否关联任务
            if not re.search(r'#\d+|\[NOTION-[\w-]+\]', commit.message):
                result.warnings.append(
                    f"[{commit.hash[:7]}] 建议关联 Story/Task ID"
                )
            
            # 检查类型
            type_match = re.match(r'^(\w+)(?:\(|:)', commit.message)
            if type_match:
                commit_type = type_match.group(1)
                if commit_type not in self.VALID_TYPES:
                    result.warnings.append(
                        f"[{commit.hash[:7]}] 未知提交类型: {commit_type}"
                    )
        
        return result
    
    def analyze_commit_frequency(self, commits: List[CommitInfo]) -> GitCheckResult:
        """分析提交频率异常"""
        result = GitCheckResult([], [], [], {})
        
        # 按作者分组
        by_author: Dict[str, List[CommitInfo]] = {}
        for commit in commits:
            by_author.setdefault(commit.author, []).append(commit)
        
        for author, author_commits in by_author.items():
            # 检测批量提交
            for commit in author_commits:
                if commit.files_changed > 20:
                    result.warnings.append(
                        f"[{commit.hash[:7]}] {author} 批量修改 {commit.files_changed} 个文件，建议分解提交"
                    )
            
            # 检测深夜提交
            for commit in author_commits:
                hour = commit.timestamp.hour
                if hour < 6 or hour > 23:
                    result.info.append(
                        f"[{commit.hash[:7]}] {author} 非工作时间提交 ({commit.timestamp.strftime('%H:%M')})"
                    )
        
        return result
    
    def calculate_contribution_stats(self, commits: List[CommitInfo]) -> Dict:
        """计算贡献统计"""
        stats = {
            'total_commits': len(commits),
            'by_role': {},
            'by_type': {}
        }
        
        for commit in commits:
            # 按角色统计
            role = self.ROLE_MAPPING.get(commit.author.lower(), '其他')
            if role not in stats['by_role']:
                stats['by_role'][role] = {
                    'commits': 0,
                    'files': 0,
                    'insertions': 0,
                    'deletions': 0
                }
            
            stats['by_role'][role]['commits'] += 1
            stats['by_role'][role]['files'] += commit.files_changed
            stats['by_role'][role]['insertions'] += commit.insertions
            stats['by_role'][role]['deletions'] += commit.deletions
            
            # 按类型统计
            type_match = re.match(r'^(\w+)(?:\(|:)', commit.message)
            if type_match:
                commit_type = type_match.group(1)
                if commit_type not in stats['by_type']:
                    stats['by_type'][commit_type] = 0
                stats['by_type'][commit_type] += 1
        
        return stats
    
    def check_branch_compliance(self) -> GitCheckResult:
        """检查分支策略合规性"""
        result = GitCheckResult([], [], [], {})
        
        # 获取所有分支
        cmd = ['git', 'branch', '-a']
        output = subprocess.check_output(cmd, cwd=self.repo_path).decode('utf-8')
        branches = [b.strip().strip('* ') for b in output.strip().split('\n')]
        
        # 分支命名规范
        valid_patterns = [
            r'^main$',
            r'^develop$',
            r'^feature/[a-z0-9-]+$',
            r'^hotfix/[a-z0-9-]+$',
            r'^release/v\d+\.\d+\.\d+$'
        ]
        
        for branch in branches:
            branch_name = branch.replace('remotes/origin/', '')
            if not any(re.match(p, branch_name) for p in valid_patterns):
                result.warnings.append(f"分支命名不符合规范: {branch_name}")
        
        # 检查 main 分支是否受保护
        # 注意：实际检查需要 GitHub/GitLab API
        
        return result
```

#### 6.2.2 文档校验模块 (document_checker.py)

```python
"""
文档更新校验模块
"""

import os
import re
import yaml
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class DocumentCheckResult:
    errors: List[str]
    warnings: List[str]
    info: List[str]

class DocumentChecker:
    """文档合规检查器"""
    
    # 关键文档路径模式
    CRITICAL_DOCS = [
        'agents/*/IDENTITY.md',
        'workflows/*.md',
        'notion/*.md',
        'skills/**/README.md',
        'governance/*.md',
        '*.md'
    ]
    
    # 模板规则
    TEMPLATE_RULES = {
        'agents/*/IDENTITY.md': {
            'required_frontmatter': ['name', 'description'],
            'required_keywords': ['官方职位', '核心权责', '汇报关系']
        },
        'workflows/*.md': {
            'required_sections': ['流程概述', '执行步骤'],
            'required_keywords': ['负责人', '输入', '输出']
        }
    }
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def run_all_checks(self) -> DocumentCheckResult:
        """运行所有文档检查"""
        result = DocumentCheckResult([], [], [])
        
        # 1. 时间戳检查
        ts_result = self.check_timestamps()
        result.errors.extend(ts_result.errors)
        result.warnings.extend(ts_result.warnings)
        
        # 2. 模板合规检查
        for doc_path in self._find_document_files():
            template_result = self.check_template_compliance(doc_path)
            result.errors.extend(template_result.errors)
            result.warnings.extend(template_result.warnings)
        
        # 3. 版本关联检查
        version_result = self.check_version_association()
        result.errors.extend(version_result.errors)
        result.warnings.extend(version_result.warnings)
        
        return result
    
    def _find_document_files(self) -> List[str]:
        """查找所有 Markdown 文档"""
        docs = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith('.md'):
                    docs.append(os.path.join(root, file))
        return docs
    
    def check_timestamps(self) -> DocumentCheckResult:
        """检查文档时间戳"""
        result = DocumentCheckResult([], [], [])
        
        import subprocess
        
        for doc_path in self._find_document_files():
            rel_path = os.path.relpath(doc_path, self.repo_path)
            
            # 获取文件修改时间
            file_mtime = os.path.getmtime(doc_path)
            
            # 获取 Git 最后提交时间
            try:
                cmd = ['git', 'log', '-1', '--format=%at', '--', rel_path]
                git_timestamp = subprocess.check_output(
                    cmd, cwd=self.repo_path
                ).decode().strip()
                
                if git_timestamp:
                    git_mtime = int(git_timestamp)
                    time_diff = abs(file_mtime - git_mtime)
                    
                    if time_diff > 60:  # 超过60秒差异
                        result.warnings.append(
                            f"[{rel_path}] 文件时间与 Git 提交时间不一致"
                        )
            except subprocess.CalledProcessError:
                pass
            
            # 检查 90 天未更新的文档
            days_since_update = (datetime.now().timestamp() - file_mtime) / 86400
            if days_since_update > 90:
                result.warnings.append(
                    f"[{rel_path}] 文档超过90天未更新，建议审查"
                )
        
        return result
    
    def check_template_compliance(self, doc_path: str) -> DocumentCheckResult:
        """检查文档模板合规性"""
        result = DocumentCheckResult([], [], [])
        rel_path = os.path.relpath(doc_path, self.repo_path)
        
        # 读取文件内容
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配适用的规则
        applicable_rules = None
        for pattern, rules in self.TEMPLATE_RULES.items():
            if self._match_pattern(rel_path, pattern):
                applicable_rules = rules
                break
        
        if not applicable_rules:
            return result
        
        # 检查 Frontmatter
        if 'required_frontmatter' in applicable_rules:
            frontmatter = self._extract_frontmatter(content)
            for key in applicable_rules['required_frontmatter']:
                if key not in frontmatter:
                    result.errors.append(f"[{rel_path}] 缺少 Frontmatter 字段: {key}")
        
        # 检查必需关键词
        if 'required_keywords' in applicable_rules:
            for keyword in applicable_rules['required_keywords']:
                if keyword not in content:
                    result.errors.append(f"[{rel_path}] 缺少关键内容: {keyword}")
        
        return result
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """提取 YAML Frontmatter"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    return yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    pass
        return {}
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """匹配路径模式"""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def check_version_association(self) -> DocumentCheckResult:
        """检查文档版本与 Git 关联"""
        result = DocumentCheckResult([], [], [])
        # 实现版本关联检查逻辑
        return result
```

#### 6.2.3 Notion 校验模块 (notion_checker.py)

```python
"""
Notion 看板校验模块
"""

import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

# Notion 数据库 ID 配置（从环境变量读取）
NOTION_DB_IDS = {
    'external_req': os.getenv('NOTION_EXTERNAL_REQ_DB_ID'),
    'story': os.getenv('NOTION_STORY_DB_ID'),
    'task': os.getenv('NOTION_TASK_DB_ID'),
    'bug': os.getenv('NOTION_BUG_DB_ID'),
    'iteration': os.getenv('NOTION_ITERATION_DB_ID'),
    'retro': os.getenv('NOTION_RETROSPECTIVE_DB_ID')
}

@dataclass
class NotionCheckResult:
    errors: List[Dict]
    warnings: List[Dict]
    info: List[Dict]
    stats: Dict

class NotionChecker:
    """Notion 看板合规检查器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = NotionClient(api_key)
    
    def run_all_checks(self) -> NotionCheckResult:
        """运行所有 Notion 检查"""
        result = NotionCheckResult([], [], [], {})
        
        # 1. 外部需求检查
        ext_result = self.check_external_requirements()
        result.errors.extend(ext_result.errors)
        result.warnings.extend(ext_result.warnings)
        
        # 2. Story/Task 检查
        story_result = self.check_stories_and_tasks()
        result.errors.extend(story_result.errors)
        result.warnings.extend(story_result.warnings)
        
        # 3. Bug 检查
        bug_result = self.check_bugs()
        result.errors.extend(bug_result.errors)
        result.warnings.extend(bug_result.warnings)
        
        # 4. 复盘检查
        retro_result = self.check_retrospectives()
        result.errors.extend(retro_result.errors)
        result.warnings.extend(retro_result.warnings)
        
        # 5. 状态流转检查
        transition_result = self.check_state_transitions()
        result.errors.extend(transition_result.errors)
        
        return result
    
    def check_external_requirements(self) -> NotionCheckResult:
        """检查外部需求登记"""
        result = NotionCheckResult([], [], [], {})
        
        db_id = NOTION_DB_IDS.get('external_req')
        if not db_id:
            result.errors.append({'message': '未配置外部需求看板 ID'})
            return result
        
        requirements = self.client.query_database(db_id)
        
        required_fields = ['需求标题', '需求描述', '来源渠道', '优先级', '状态']
        
        for req in requirements:
            req_id = req['id']
            props = req.get('properties', {})
            
            # 检查必填字段
            for field in required_fields:
                if not self._has_property_value(props, field):
                    result.errors.append({
                        'id': req_id,
                        'message': f"缺少必填字段: {field}"
                    })
            
            # 检查已采纳需求是否关联 Story
            status = self._get_status(props, '状态')
            if status == '已采纳':
                related = self._get_relation(props, '关联需求')
                if not related:
                    result.errors.append({
                        'id': req_id,
                        'message': "已采纳但未关联 Story"
                    })
        
        return result
    
    def check_stories_and_tasks(self) -> NotionCheckResult:
        """检查 Story 和 Task"""
        result = NotionCheckResult([], [], [], {})
        
        # 检查 Story
        story_db = NOTION_DB_IDS.get('story')
        if story_db:
            stories = self.client.query_database(story_db)
            for story in stories:
                story_id = story['id']
                props = story.get('properties', {})
                
                # 检查标题格式
                title = self._get_title(props)
                if title and not title.startswith('['):
                    result.warnings.append({
                        'id': story_id,
                        'message': f"Story 标题建议以 [模块] 开头: {title[:30]}"
                    })
        
        # 检查 Task
        task_db = NOTION_DB_IDS.get('task')
        if task_db:
            tasks = self.client.query_database(task_db)
            for task in tasks:
                task_id = task['id']
                props = task.get('properties', {})
                
                status = self._get_status(props, '状态')
                
                # 检查已完成 Task 的时间记录
                if status == '已完成':
                    if not self._has_property_value(props, '结束时间'):
                        result.errors.append({
                            'id': task_id,
                            'message': "已完成 Task 必须记录结束时间"
                        })
        
        return result
    
    def check_bugs(self) -> NotionCheckResult:
        """检查 Bug 记录"""
        result = NotionCheckResult([], [], [], {})
        
        db_id = NOTION_DB_IDS.get('bug')
        if not db_id:
            return result
        
        bugs = self.client.query_database(db_id)
        
        for bug in bugs:
            bug_id = bug['id']
            props = bug.get('properties', {})
            status = self._get_status(props, '状态')
            
            # 检查已修复 Bug
            if status in ['已修复', '已验证']:
                if not self._has_property_value(props, '修复时间'):
                    result.errors.append({
                        'id': bug_id,
                        'message': "已修复 Bug 必须记录修复时间"
                    })
                
                if not self._has_property_value(props, '负责人'):
                    result.errors.append({
                        'id': bug_id,
                        'message': "已修复 Bug 必须记录修复负责人"
                    })
        
        return result
    
    def check_retrospectives(self) -> NotionCheckResult:
        """检查每日复盘"""
        result = NotionCheckResult([], [], [], {})
        
        db_id = NOTION_DB_IDS.get('retro')
        if not db_id:
            return result
        
        retros = self.client.query_database(db_id)
        
        # 获取实际复盘日期
        retro_dates = set()
        for retro in retros:
            retro_date = self._get_date(retro.get('properties', {}), '复盘日期(日期)')
            if retro_date:
                retro_dates.add(retro_date)
        
        # 检查缺失的复盘（最近14个工作日）
        today = date.today()
        for i in range(14):
            check_date = today - timedelta(days=i)
            if check_date.weekday() >= 5:  # 跳过周末
                continue
            if check_date not in retro_dates:
                result.errors.append({
                    'id': 'N/A',
                    'message': f"缺少 {check_date} 的复盘记录"
                })
        
        return result
    
    def check_state_transitions(self) -> NotionCheckResult:
        """检查状态流转合规性"""
        result = NotionCheckResult([], [], [], {})
        # 实现状态流转检查
        return result
    
    # 辅助方法
    def _has_property_value(self, props: Dict, name: str) -> bool:
        """检查属性是否有值"""
        prop = props.get(name)
        if not prop:
            return False
        
        prop_type = prop.get('type')
        if prop_type == 'title':
            return bool(prop.get('title', []))
        elif prop_type == 'rich_text':
            return bool(prop.get('rich_text', []))
        elif prop_type == 'select':
            return prop.get('select') is not None
        elif prop_type == 'status':
            return prop.get('status', {}).get('name') is not None
        elif prop_type == 'date':
            return prop.get('date') is not None
        elif prop_type == 'relation':
            return bool(prop.get('relation', []))
        return False
    
    def _get_status(self, props: Dict, name: str) -> Optional[str]:
        """获取状态值"""
        prop = props.get(name, {})
        if prop.get('type') == 'status':
            return prop.get('status', {}).get('name')
        return None
    
    def _get_title(self, props: Dict) -> Optional[str]:
        """获取标题"""
        for key, value in props.items():
            if value.get('type') == 'title':
                title_parts = value.get('title', [])
                if title_parts:
                    return ''.join(p.get('plain_text', '') for p in title_parts)
        return None
    
    def _get_relation(self, props: Dict, name: str) -> List:
        """获取关联值"""
        prop = props.get(name, {})
        if prop.get('type') == 'relation':
            return prop.get('relation', [])
        return []
    
    def _get_date(self, props: Dict, name: str) -> Optional[date]:
        """获取日期值"""
        prop = props.get(name, {})
        if prop.get('type') == 'date':
            date_str = prop.get('date', {}).get('start')
            if date_str:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
        return None


class NotionClient:
    """Notion API 客户端（简化版）"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
    
    def query_database(self, database_id: str) -> List[Dict]:
        """查询数据库"""
        import requests
        
        url = f"{self.base_url}/databases/{database_id}/query"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        results = []
        has_more = True
        start_cursor = None
        
        while has_more:
            payload = {}
            if start_cursor:
                payload["start_cursor"] = start_cursor
            
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            
            results.extend(data.get('results', []))
            has_more = data.get('has_more', False)
            start_cursor = data.get('next_cursor')
        
        return results
```

#### 6.2.4 复盘校验模块 (retro_checker.py)

```python
"""
复盘同步校验模块
"""

import re
from datetime import date, timedelta
from typing import List, Dict, Set
from dataclasses import dataclass

@dataclass
class RetroCheckResult:
    errors: List[Dict]
    warnings: List[Dict]
    info: List[Dict]
    summary: Dict

class RetroChecker:
    """复盘同步检查器"""
    
    def __init__(self, notion_checker: 'NotionChecker'):
        self.notion = notion_checker
    
    def run_all_checks(self) -> RetroCheckResult:
        """运行所有复盘检查"""
        result = RetroCheckResult([], [], [], {})
        
        # 1. 复盘与 Task/Bug 关联性
        assoc_result = self.check_retro_task_bug_association()
        result.errors.extend(assoc_result.errors)
        result.warnings.extend(assoc_result.warnings)
        
        # 2. 改进项跟进
        followup_result = self.check_improvement_items()
        result.errors.extend(followup_result.errors)
        result.warnings.extend(followup_result.warnings)
        
        # 3. Token 开销记录
        token_result = self.check_token_recording()
        result.warnings.extend(token_result.warnings)
        
        # 4. 周期合规性
        cycle_result = self.check_cycle_compliance()
        result.errors.extend(cycle_result.errors)
        result.summary.update(cycle_result.summary)
        
        return result
    
    def check_retro_task_bug_association(self) -> RetroCheckResult:
        """检查复盘与 Task/Bug 关联性"""
        result = RetroCheckResult([], [], [], {})
        
        retros = self.notion.client.query_database(NOTION_DB_IDS['retro'])
        
        for retro in retros:
            retro_id = retro['id']
            props = retro.get('properties', {})
            
            retro_date = self.notion._get_date(props, '复盘日期(日期)')
            if not retro_date:
                continue
            
            # 获取当日产出文本
            output = self._get_rich_text(props, '当日产出')
            
            # 提取提及的 Task/Bug ID
            mentioned_ids = self._extract_ids(output)
            
            # 获取当日实际完成的 Task/Bug
            completed_tasks = self._get_completed_tasks_on_date(retro_date)
            completed_bugs = self._get_completed_bugs_on_date(retro_date)
            
            # 检查覆盖度
            task_ids = {t['id'] for t in completed_tasks}
            mentioned_task_ids = set(mentioned_ids.get('tasks', []))
            
            if task_ids and len(mentioned_task_ids & task_ids) / len(task_ids) < 0.5:
                result.warnings.append({
                    'id': retro_id,
                    'message': f"复盘对 Task 的覆盖度偏低，当日完成 {len(task_ids)} 个"
                })
        
        return result
    
    def check_improvement_items(self) -> RetroCheckResult:
        """检查改进项跟进"""
        result = RetroCheckResult([], [], [], {})
        
        retros = self.notion.client.query_database(NOTION_DB_IDS['retro'])
        
        all_items = []
        for retro in retros:
            retro_id = retro['id']
            props = retro.get('properties', {})
            
            improvements_text = self._get_rich_text(props, '改进项')
            if improvements_text:
                items = self._parse_improvement_items(improvements_text)
                all_items.extend(items)
        
        # 检查超期改进项
        overdue_count = 0
        for item in all_items:
            if item.get('deadline') and item['deadline'] < date.today():
                if item.get('status') not in ['已完成', '已放弃']:
                    overdue_count += 1
                    result.errors.append({
                        'id': 'N/A',
                        'message': f"改进项超期: {item['description'][:50]}"
                    })
        
        result.summary['total_improvements'] = len(all_items)
        result.summary['overdue_improvements'] = overdue_count
        
        return result
    
    def check_token_recording(self) -> RetroCheckResult:
        """检查 Token 开销记录"""
        result = RetroCheckResult([], [], [], {})
        # 实现 Token 开销检查逻辑
        return result
    
    def check_cycle_compliance(self) -> RetroCheckResult:
        """检查复盘周期合规性"""
        result = RetroCheckResult([], [], [], {})
        
        retros = self.notion.client.query_database(NOTION_DB_IDS['retro'])
        
        # 收集复盘日期
        retro_dates = set()
        for retro in retros:
            props = retro.get('properties', {})
            retro_date = self.notion._get_date(props, '复盘日期(日期)')
            if retro_date:
                retro_dates.add(retro_date)
        
        # 计算最近14个工作日的合规率
        today = date.today()
        expected_days = 0
        actual_days = 0
        
        for i in range(20):  # 检查最近20天
            check_date = today - timedelta(days=i)
            if check_date.weekday() >= 5:  # 跳过周末
                continue
            expected_days += 1
            if check_date in retro_dates:
                actual_days += 1
            else:
                result.errors.append({
                    'id': 'N/A',
                    'message': f"缺少 {check_date} 的复盘记录"
                })
        
        compliance_rate = actual_days / expected_days if expected_days > 0 else 0
        result.summary['compliance_rate'] = f"{compliance_rate*100:.1f}%"
        result.summary['expected_days'] = expected_days
        result.summary['actual_days'] = actual_days
        
        return result
    
    # 辅助方法
    def _get_rich_text(self, props: Dict, name: str) -> str:
        """获取富文本内容"""
        prop = props.get(name, {})
        if prop.get('type') == 'rich_text':
            texts = prop.get('rich_text', [])
            return ''.join(t.get('plain_text', '') for t in texts)
        return ''
    
    def _extract_ids(self, text: str) -> Dict[str, List[str]]:
        """从文本中提取 Task/Bug ID"""
        result = {'tasks': [], 'bugs': []}
        
        # 匹配 Task 引用 (如 TASK-123, #123)
        task_pattern = r'(?:TASK-|#)(\d+)'
        result['tasks'] = re.findall(task_pattern, text)
        
        # 匹配 Bug 引用 (如 BUG-123)
        bug_pattern = r'BUG-(\d+)'
        result['bugs'] = re.findall(bug_pattern, text)
        
        return result
    
    def _parse_improvement_items(self, text: str) -> List[Dict]:
        """解析改进项文本"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                # 简单解析格式: - 改进内容 [负责人] [截止日期]
                item = {'description': line[1:].strip(), 'status': '待处理'}
                
                # 提取负责人
                owner_match = re.search(r'\[([^\]]+)\]', line)
                if owner_match:
                    item['owner'] = owner_match.group(1)
                
                items.append(item)
        
        return items
    
    def _get_completed_tasks_on_date(self, target_date: date) -> List[Dict]:
        """获取指定日期完成的 Task"""
        # 通过 Notion API 查询
        tasks = self.notion.client.query_database(NOTION_DB_IDS['task'])
        completed = []
        
        for task in tasks:
            props = task.get('properties', {})
            end_date = self.notion._get_date(props, '结束时间')
            status = self.notion._get_status(props, '状态')
            
            if status == '已完成' and end_date == target_date:
                completed.append(task)
        
        return completed
    
    def _get_completed_bugs_on_date(self, target_date: date) -> List[Dict]:
        """获取指定日期完成的 Bug"""
        bugs = self.notion.client.query_database(NOTION_DB_IDS['bug'])
        completed = []
        
        for bug in bugs:
            props = bug.get('properties', {})
            fix_date = self.notion._get_date(props, '修复时间')
            status = self.notion._get_status(props, '状态')
            
            if status == '已验证' and fix_date == target_date:
                completed.append(bug)
        
        return completed
```

### 6.3 检查项清单（Checklist）

#### 6.3.1 Git 提交检查项

| 类别 | 检查项 | 级别 | 检查频率 |
|-----|-------|-----|---------|
| 提交信息 | 提交信息符合 Conventional Commits 格式 | 错误 | 每次提交 |
| 提交信息 | 提交主题长度不超过72字符 | 警告 | 每次提交 |
| 提交信息 | 提交关联 Story/Task ID | 警告 | 每次提交 |
| 提交信息 | 提交类型与修改文件匹配 | 警告 | 每次提交 |
| 提交频率 | 单次提交修改文件数不超过20个 | 警告 | 每日 |
| 提交频率 | 提交频率符合角色基线 | 信息 | 每周 |
| 改动量 | 重构代码单次不超过500行 | 警告 | 每次提交 |
| 改动量 | 文档与功能改动比例 >= 1:3 | 警告 | 每周 |
| 分支策略 | 分支命名符合规范 | 错误 | 每日 |
| 分支策略 | main 分支受保护 | 错误 | 每日 |
| 分支策略 | 清理30天无活动的分支 | 警告 | 每周 |

#### 6.3.2 文档更新检查项

| 类别 | 检查项 | 级别 | 检查频率 |
|-----|-------|-----|---------|
| 时间戳 | 文件修改时间与 Git 提交一致 | 警告 | 每日 |
| 时效性 | 关键文档90天内更新 | 警告 | 每周 |
| 版本关联 | 文档版本号符合 SemVer | 错误 | 每次提交 |
| 版本关联 | 关联提交哈希有效 | 错误 | 每日 |
| 审批流程 | L2+ 变更通过 PR | 错误 | 每次提交 |
| 审批流程 | L2+ 变更有 Review | 错误 | 每次提交 |
| 模板合规 | 包含必需 Frontmatter | 错误 | 每次提交 |
| 模板合规 | 包含必需章节 | 错误 | 每次提交 |
| 模板合规 | 包含关键内容关键词 | 错误 | 每次提交 |

#### 6.3.3 Notion 看板检查项

| 类别 | 检查项 | 级别 | 检查频率 |
|-----|-------|-----|---------|
| 外部需求 | 必填字段完整 | 错误 | 每日 |
| 外部需求 | 已采纳需求关联 Story | 错误 | 每日 |
| 外部需求 | 状态流转符合 SLA | 警告 | 每日 |
| Story | 必填字段完整 | 错误 | 每日 |
| Story | 进行中/已完成 Story 有关联 Task | 警告 | 每日 |
| Story | 非待开发状态关联迭代 | 错误 | 每日 |
| Task | 必填字段完整 | 错误 | 每日 |
| Task | 已完成 Task 记录结束时间 | 错误 | 每日 |
| Task | 已完成 Task 记录实际工时 | 警告 | 每日 |
| Bug | 必填字段完整 | 错误 | 每日 |
| Bug | 已修复 Bug 记录修复时间 | 错误 | 每日 |
| Bug | 已修复 Bug 记录修复说明 | 警告 | 每日 |
| 复盘 | 每日复盘按时创建 | 错误 | 每日 |
| 复盘 | 复盘关联对应迭代 | 警告 | 每日 |
| 复盘 | 复盘包含当日产出 | 错误 | 每日 |

#### 6.3.4 复盘同步检查项

| 类别 | 检查项 | 级别 | 检查频率 |
|-----|-------|-----|---------|
| 关联性 | 复盘覆盖当日完成 Task | 警告 | 每日 |
| 关联性 | 复盘覆盖当日修复 Bug | 警告 | 每日 |
| 关联性 | 阻塞问题状态一致 | 警告 | 每日 |
| 改进项 | 改进项指定负责人 | 警告 | 每日 |
| 改进项 | 改进项在截止日期前完成 | 错误 | 每周 |
| 改进项 | 改进项闭环率 >= 80% | 警告 | 迭代末 |
| Token | Token 开销记录完整 | 警告 | 每日 |
| 周期 | 工作日复盘率 = 100% | 错误 | 每周 |
| 周期 | 复盘在次日18:00前创建 | 警告 | 每日 |

### 6.4 输出报告格式

#### 6.4.1 报告结构

```yaml
# 报告结构定义
report:
  metadata:
    generated_at: "2026-03-27T18:00:00+08:00"
    report_type: "daily" | "weekly" | "iteration"
    checker_version: "1.0.0"
    period:
      start: "2026-03-20"
      end: "2026-03-27"
  
  summary:
    total_checks: 150
    passed: 135
    warnings: 12
    errors: 3
    compliance_rate: "90.0%"
  
  sections:
    - name: "Git 提交校验"
      status: "passed" | "warning" | "error"
      summary:
        total_commits: 45
        errors: 1
        warnings: 3
      details: []
    
    - name: "文档更新校验"
      status: "passed"
      summary:
        documents_checked: 25
        errors: 0
        warnings: 2
      details: []
    
    - name: "Notion 看板校验"
      status: "warning"
      summary:
        records_checked: 80
        errors: 2
        warnings: 5
      details: []
    
    - name: "复盘同步校验"
      status: "passed"
      summary:
        retrospectives_checked: 7
        errors: 0
        warnings: 2
      details: []
  
  action_items:
    - priority: "high"
      description: "修复 Bug #123 的修复时间缺失问题"
      owner: "zhoubo"
      due_date: "2026-03-28"
    
    - priority: "medium"
      description: "补充 2026-03-25 的复盘记录"
      owner: "lujia"
      due_date: "2026-03-28"
```

#### 6.4.2 Markdown 报告模板

```markdown
# 留痕校验报告

> **报告类型**: 日报  
> **检查周期**: 2026-03-20 至 2026-03-27  
> **生成时间**: 2026-03-27 18:00:00  
> **校验版本**: v1.0.0

---

## 📊 总体概览

| 指标 | 数值 |
|-----|------|
| 总检查项 | 150 |
| 通过 | 135 ✅ |
| 警告 | 12 ⚠️ |
| 错误 | 3 ❌ |
| 合规率 | 90.0% |

---

## 🔍 详细检查结果

### 1. Git 提交校验

**状态**: ⚠️ 警告

| 检查项 | 结果 | 说明 |
|-------|------|------|
| 提交信息规范 | ✅ 通过 | 45/45 符合规范 |
| 提交频率 | ⚠️ 警告 | 发现 1 次批量提交 |
| 改动量统计 | ✅ 通过 | 各角色贡献正常 |
| 分支策略 | ❌ 错误 | 发现 1 个不合规分支 |

**详细问题**:
1. ❌ [abc1234] 分支 `feature/temp-branch` 命名不符合规范
2. ⚠️ [def5678] 批量修改 25 个文件，建议分解
3. ⚠️ [ghi9012] 建议关联 Story/Task ID

---

### 2. 文档更新校验

**状态**: ✅ 通过

| 检查项 | 结果 | 说明 |
|-------|------|------|
| 时间戳检查 | ✅ 通过 | 所有文档时间戳一致 |
| 版本关联 | ✅ 通过 | 版本号符合规范 |
| 模板合规 | ⚠️ 警告 | 2 个文档缺少章节 |

---

### 3. Notion 看板校验

**状态**: ❌ 错误

**外部需求看板**:
- ✅ 10 条记录，全部合规

**Story/Task 看板**:
- ⚠️ 3 个 Task 缺少结束时间

**Bug 看板**:
- ❌ 2 个已修复 Bug 缺少修复时间

**每日复盘**:
- ❌ 缺少 2026-03-25 的复盘记录

---

### 4. 复盘同步校验

**状态**: ✅ 通过

| 检查项 | 结果 | 说明 |
|-------|------|------|
| Task/Bug 关联 | ✅ 通过 | 覆盖率 85% |
| 改进项跟进 | ⚠️ 警告 | 2 个改进项临近截止 |
| 周期合规 | ✅ 通过 | 复盘率 100% |

---

## 📋 待办事项

| 优先级 | 事项 | 负责人 | 截止日期 | 状态 |
|-------|------|-------|---------|------|
| 🔴 高 | 修复 Bug #123 修复时间缺失 | zhoubo | 2026-03-28 | 待处理 |
| 🔴 高 | 补充 2026-03-25 复盘记录 | lujia | 2026-03-28 | 待处理 |
| 🟡 中 | 规范分支命名 | hanxin | 2026-03-29 | 待处理 |

---

## 📈 趋势分析

```
合规率趋势（最近7天）

100% |                    █
 90% |    █    █    █    █
 80% |    █    █    █    █
     +----+----+----+----+----+----+----
       D1   D2   D3   D4   D5   D6   D7
```

---

*报告由 InfinityCompany 留痕校验系统自动生成*
```

### 6.5 自动化触发建议

#### 6.5.1 Git Hooks 配置

```bash
#!/bin/bash
# .git/hooks/commit-msg
# 提交信息预检查

python scripts/traceability/core/git_checker.py --hook commit-msg "$1"
```

```bash
#!/bin/bash
# .git/hooks/pre-push
# 推送前检查

python scripts/traceability/main.py --check git --fail-on-error
```

#### 6.5.2 定时任务配置 (Cron)

```bash
# crontab -e

# 每日 18:30 执行日常检查（周勃环境检查后）
30 18 * * * cd /path/to/InfinityCompany && python scripts/traceability/main.py --report daily >> logs/traceability.log 2>&1

# 每周五 19:00 执行周检查
0 19 * * 5 cd /path/to/InfinityCompany && python scripts/traceability/main.py --report weekly --notify

# 每月 1 号 09:00 执行月度检查
0 9 1 * * cd /path/to/InfinityCompany && python scripts/traceability/main.py --report monthly --notify
```

#### 6.5.3 GitHub Actions 配置

```yaml
# .github/workflows/traceability-check.yml
name: Traceability Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # 每日 18:30 运行
    - cron: '30 18 * * *'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r scripts/traceability/requirements.txt
      
      - name: Run traceability checks
        env:
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
          NOTION_STORY_DB_ID: ${{ secrets.NOTION_STORY_DB_ID }}
          NOTION_TASK_DB_ID: ${{ secrets.NOTION_TASK_DB_ID }}
          NOTION_BUG_DB_ID: ${{ secrets.NOTION_BUG_DB_ID }}
          NOTION_ITERATION_DB_ID: ${{ secrets.NOTION_ITERATION_DB_ID }}
          NOTION_RETROSPECTIVE_DB_ID: ${{ secrets.NOTION_RETROSPECTIVE_DB_ID }}
          NOTION_EXTERNAL_REQ_DB_ID: ${{ secrets.NOTION_EXTERNAL_REQ_DB_ID }}
        run: |
          python scripts/traceability/main.py --report daily --format markdown --output reports/
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: traceability-report
          path: reports/
      
      - name: Notify on failure
        if: failure()
        uses: slack-action@v1
        with:
          webhook: ${{ secrets.SLACK_WEBHOOK }}
          message: "❌ 留痕校验失败，请检查报告"
```

---

## 7. 校验执行计划

### 7.1 校验频率建议

| 校验类型 | 频率 | 触发方式 | 执行时间 | 责任人 |
|---------|-----|---------|---------|-------|
| Git 提交信息 | 实时 | Git Hook (commit-msg) | 每次提交 | 自动 |
| Git 分支策略 | 每日 | Git Hook (pre-push) | 每次推送 | 自动 |
| Git 统计汇总 | 每日 | Cron / CI | 18:30 | 自动 |
| 文档时间戳 | 每日 | Cron | 18:30 | 自动 |
| 文档模板合规 | 每次提交 | CI / 本地脚本 | PR 时 | 自动 |
| Notion 必填字段 | 每日 | Cron | 18:30 | 自动 |
| Notion 状态流转 | 每日 | Cron | 18:30 | 自动 |
| Notion SLA 检查 | 每日 | Cron | 18:30 | 自动 |
| 复盘关联性 | 每日 | Cron | 18:30 | 自动 |
| 改进项跟进 | 每周 | Cron (周五) | 19:00 | 自动 |
| 全面合规检查 | 迭代末 | 手动触发 | - | 曹参(PMO) |
| 季度审计 | 每季度 | 手动触发 | - | 陆贾(知识库) |

### 7.2 各校验项责任人分配

| 校验领域 | 负责人 | 职责说明 |
|---------|-------|---------|
| Git 提交规范 | 萧何(架构师) | 制定代码提交规范，审核规范执行 |
| 文档更新校验 | 陆贾(知识库) | 维护文档模板，审核文档合规性 |
| Notion 看板 | 曹参(PMO) | 监控看板数据质量，处理异常 |
| 复盘同步 | 曹参(PMO) | 确保复盘按时完成，改进项跟进 |
| 脚本维护 | 周勃(运维) | 维护校验脚本，配置自动化 |
| 异常处理 | 夏侯婴(私人助理) | 分发异常告警，跟踪处理进度 |
| 合规审计 | 张良(产品经理) | 定期审查整体合规情况 |

### 7.3 异常处理流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         留痕校验异常处理流程                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐                                                           │
│  │ 校验发现异常 │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         异常分级                                     │   │
│  ├─────────────────┬─────────────────┬─────────────────────────────────┤   │
│  │   🔴 错误级别    │   🟡 警告级别    │         ℹ️ 信息级别            │   │
│  ├─────────────────┼─────────────────┼─────────────────────────────────┤   │
│  │ • 必填字段缺失  │ • 建议性改进     │ • 统计信息                      │   │
│  │ • 非法状态流转  │ • 格式建议       │ • 趋势分析                      │   │
│  │ • 严重超时      │ • 覆盖度偏低     │ • 正常提醒                      │   │
│  └────────┬────────┴────────┬────────┴───────────────┬─────────────────┘   │
│           │                 │                        │                     │
│           ▼                 ▼                        ▼                     │
│  ┌─────────────────┐ ┌─────────────────┐  ┌─────────────────┐             │
│  │ 立即通知负责人  │ │ 记录到日报      │  │ 仅记录日志      │             │
│  │ 创建修复 Task   │ │ 定时汇总提醒    │  │ 不主动通知      │             │
│  │ 阻塞相关流程    │ │ 不阻塞流程      │  │ 不阻塞流程      │             │
│  └────────┬────────┘ └────────┬────────┘  └─────────────────┘             │
│           │                   │                                            │
│           └─────────┬─────────┘                                            │
│                     ▼                                                      │
│            ┌─────────────────┐                                             │
│            │  夏侯婴分发告警  │                                             │
│            │  根据类型路由到  │                                             │
│            │  对应角色处理    │                                             │
│            └────────┬────────┘                                             │
│                     │                                                      │
│                     ▼                                                      │
│            ┌─────────────────┐                                             │
│            │  责任人处理问题  │                                             │
│            │  更新修复状态    │                                             │
│            └────────┬────────┘                                             │
│                     │                                                      │
│                     ▼                                                      │
│            ┌─────────────────┐                                             │
│            │  陆贾验证修复    │                                             │
│            │  更新知识库      │                                             │
│            │  记录改进项      │                                             │
│            └─────────────────┘                                             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

#### 7.3.1 告警通知规则

| 异常级别 | 通知方式 | 通知对象 | 响应时效 |
|---------|---------|---------|---------|
| 🔴 错误 | Slack DM + 邮件 + Notion 评论 | 直接责任人 + PMO | 4 小时内 |
| 🟡 警告 | Slack 频道 + 日报汇总 | 相关角色 | 24 小时内 |
| ℹ️ 信息 | 日报汇总 | 全员 | 无需响应 |

#### 7.3.2 修复 SLA

| 异常类型 | 修复 SLA | 升级条件 |
|---------|---------|---------|
| 必填字段缺失 | 24 小时 | 超期自动升级到 PMO |
| 状态流转异常 | 4 小时 | 超期阻塞相关流程 |
| 复盘缺失 | 24 小时 | 超期计入团队绩效 |
| 改进项超期 | 48 小时 | 超期升级到 Owner |
| 文档过期 | 1 周 | 超期标记为废弃 |

---

## 8. 附录：关键检查点清单

### 8.1 按角色划分的检查项

#### 8.1.1 韩信（全栈研发）

| 检查项 | 检查内容 | 检查时机 |
|-------|---------|---------|
| 代码提交规范 | 提交信息符合 Conventional Commits | 每次提交 |
| 代码提交关联 | 提交关联 Story/Task ID | 每次提交 |
| Task 状态更新 | 开发完成后及时更新 Task 状态 | Task 完成时 |
| 工时记录 | 记录 Task 实际工时 | Task 完成时 |
| Bug 修复记录 | 修复 Bug 时记录修复说明 | Bug 修复时 |
| 文档更新 | 功能变更同步更新相关文档 | 代码提交时 |

#### 8.1.2 张良（产品经理）

| 检查项 | 检查内容 | 检查时机 |
|-------|---------|---------|
| Story 创建规范 | Story 包含完整背景、目标、验收标准 | 创建 Story 时 |
| PRD 文档更新 | PRD 变更同步更新版本号 | 文档修改时 |
| 需求关联 | 外部需求与 Story 正确关联 | Story 创建时 |
| 验收记录 | 产品验收后记录验收结果 | Story 验收时 |

#### 8.1.3 曹参（PMO）

| 检查项 | 检查内容 | 检查时机 |
|-------|---------|---------|
| 迭代创建 | 每日创建迭代卡片 | 每日上午 |
| Task 分配 | Task 正确关联 Story 和迭代 | Task 创建时 |
| 复盘完成 | 确保每日复盘按时完成 | 每日下午 |
| 改进项跟进 | 跟踪复盘改进项完成状态 | 每周 |
| 合规报告审查 | 审查每日合规报告 | 每日 |

#### 8.1.4 陆贾（知识库管理员）

| 检查项 | 检查内容 | 检查时机 |
|-------|---------|---------|
| 文档模板合规 | 文档符合模板规范 | 文档提交时 |
| 文档版本管理 | 文档版本号正确更新 | 文档修改时 |
| 知识归档 | 发布内容及时归档 | 发布后 2 天内 |
| 文档过期检查 | 定期检查文档时效性 | 每周 |

#### 8.1.5 周勃（运维工程师）

| 检查项 | 检查内容 | 检查时机 |
|-------|---------|---------|
| 环境检查留痕 | 每日 18:00 检查结果记录 | 每日 |
| 部署记录 | 部署操作记录到迭代卡片 | 每次部署 |
| 监控告警 | 告警事件记录到 Bug 看板 | 告警发生时 |
| 脚本维护 | 校验脚本正常运行 | 持续 |
| 合规检查执行 | 确保校验任务按计划执行 | 每日 |

### 8.2 按流程阶段划分的检查项

#### 8.2.1 需求阶段（曹参 + 张良）

| 阶段 | 检查项 | 检查时机 |
|-----|-------|---------|
| 需求建卡 | Story 必填字段完整 | Story 创建时 |
| 需求建卡 | Story 关联正确迭代 | Story 创建时 |
| 需求建卡 | 外部需求来源渠道填写 | 外部需求登记时 |
| 产品定义 | PRD 文档版本号更新 | PRD 修改时 |
| 产品定义 | 验收标准明确可执行 | PRD 评审时 |

#### 8.2.2 开发阶段（韩信 + 萧何）

| 阶段 | 检查项 | 检查时机 |
|-----|-------|---------|
| 技术拆解 | Task 正确关联 Story | Task 创建时 |
| 技术拆解 | 工时预估合理 | Task 创建时 |
| 代码开发 | 提交信息符合规范 | 代码提交时 |
| 代码开发 | 代码关联 Task ID | 代码提交时 |
| 代码评审 | Review 意见记录 | PR 合并时 |
| 研发自测 | 自测结果记录 | 提测时 |

#### 8.2.3 测试阶段（陈平）

| 阶段 | 检查项 | 检查时机 |
|-----|-------|---------|
| Bug 登记 | Bug 必填字段完整 | Bug 创建时 |
| Bug 登记 | Bug 关联相关 Task | Bug 创建时 |
| Bug 登记 | 严重程度评估准确 | Bug 创建时 |
| Bug 修复 | 修复时间记录 | Bug 修复时 |
| Bug 修复 | 修复说明清晰 | Bug 修复时 |
| Bug 验证 | 验证结果记录 | Bug 验证时 |

#### 8.2.4 部署阶段（周勃）

| 阶段 | 检查项 | 检查时机 |
|-----|-------|---------|
| 部署发布 | 部署记录到迭代 | 部署时 |
| 线上验证 | 验证结果记录 | 部署后 |
| 回滚记录 | 回滚原因记录 | 回滚时 |

#### 8.2.5 复盘阶段（曹参 + 陆贾）

| 阶段 | 检查项 | 检查时机 |
|-----|-------|---------|
| 复盘记录 | 复盘按时创建 | 每日 |
| 复盘记录 | 复盘关联迭代 | 复盘创建时 |
| 复盘记录 | 当日产出完整 | 复盘完成时 |
| 复盘记录 | 阻塞问题记录 | 复盘完成时 |
| 改进项 | 改进项指定负责人 | 复盘完成时 |
| 改进项 | 改进项设定截止日期 | 复盘完成时 |
| 知识归档 | 技术方案归档 | 发布后 2 天 |
| 知识归档 | Bug 根因分析归档 | Bug 关闭后 |

---

## 9. 实施路线图

### 9.1 Phase 1: 基础设施（第 1 周）

- [ ] 创建校验脚本目录结构
- [ ] 实现 Git 提交检查 Git Hook
- [ ] 配置环境变量和依赖
- [ ] 编写基础检查模块框架

### 9.2 Phase 2: 核心功能（第 2-3 周）

- [ ] 实现 Git 校验模块完整功能
- [ ] 实现文档校验模块
- [ ] 实现 Notion API 客户端封装
- [ ] 实现 Notion 看板基础检查

### 9.3 Phase 3: 完整集成（第 4 周）

- [ ] 实现复盘同步检查
- [ ] 集成报告生成模块
- [ ] 配置定时任务和 CI
- [ ] 编写使用文档

### 9.4 Phase 4: 试运行（第 5-6 周）

- [ ] 试运行校验流程
- [ ] 收集反馈并优化
- [ ] 调整检查规则和阈值
- [ ] 培训各角色使用

### 9.5 Phase 5: 正式运行（第 7 周起）

- [ ] 正式启用全自动校验
- [ ] 建立合规审查机制
- [ ] 持续优化和改进

---

## 10. 参考文档

| 文档 | 路径 | 说明 |
|-----|------|------|
| Phase 4 报告 | `PHASE4_KNOWLEDGE_BOARD_IMPLEMENTATION_REPORT.md` | Notion 看板结构 |
| Phase 5 报告 | `PHASE5_COLLABORATION_WORKFLOW_IMPLEMENTATION_REPORT.md` | 协作流程设计 |
| 外部助理流程 | `workflows/external_assistant_workflow.md` | 外部需求处理 |
| 私人助理流程 | `workflows/personal_assistant_workflow.md` | 需求分发流程 |
| 交付闭环流程 | `workflows/internal_delivery_workflow.md` | 完整交付流程 |
| 技能接入规范 | `skills/README.md` | 技能使用指南 |
| Notion Schema | `notion/schema_definition.md` | 看板字段定义 |
| 关联规则 | `notion/relation_rules.md` | 状态流转规则 |

---

## 附录 A：可执行校验命令

### A.1 Git 提交信息快速检查命令

#### 检查最近7天的提交信息格式
```bash
# 检查提交信息是否符合 Conventional Commits
git log --since="7 days ago" --pretty=format:"%s" | grep -E '^(feat|fix|docs|style|refactor|test|chore|design|workflow|agent)(\([a-zA-Z0-9_/:-]+\))?!?: .+' | wc -l

# 检查不符合规范的提交
git log --since="7 days ago" --pretty=format:"%H %s" | while read hash msg; do
  if ! [[ "$msg" =~ ^(feat|fix|docs|style|refactor|test|chore|design|workflow|agent)(\([a-zA-Z0-9_/:-]+\))?!?:\ .+ ]]; then
    echo "不合规: $hash - $msg"
  fi
done
```

#### 按角色统计提交数量
```bash
# 按作者统计最近7天提交
git log --since="7 days ago" --pretty=format:"%an" | sort | uniq -c | sort -rn

# 按角色统计（基于用户名映射）
git log --since="7 days ago" --pretty=format:"%an" | awk '
  { count[$0]++ }
  END {
    for (author in count) {
      role = author
      if (author ~ /hanxin|韩信/) role = "韩信(研发)"
      else if (author ~ /zhangliang|张良/) role = "张良(产品)"
      else if (author ~ /xiaohe|萧何/) role = "萧何(架构)"
      else if (author ~ /zhoubo|周勃/) role = "周勃(运维)"
      else if (author ~ /caocan|曹参/) role = "曹参(PMO)"
      else if (author ~ /lujia|陆贾/) role = "陆贾(知识库)"
      else if (author ~ /chenping|陈平/) role = "陈平(测试)"
      else if (author ~ /shusuntong|叔孙通/) role = "叔孙通(设计)"
      print role ": " count[author] "次"
    }
  }'
```

#### 检查提交关联 Story/Task ID
```bash
# 检查未关联任务ID的提交
git log --since="7 days ago" --pretty=format:"%H %s" | grep -v -E '#[0-9]+|\[NOTION-[A-Z0-9-]+\]'

# 统计关联率
total=$(git log --since="7 days ago" --oneline | wc -l)
linked=$(git log --since="7 days ago" --pretty=format:"%s" | grep -E '#[0-9]+|\[NOTION-[A-Z0-9-]+\]' | wc -l)
echo "关联率: $linked/$total ($(($linked * 100 / $total))%)"
```

#### 检查分支命名规范
```bash
# 列出所有不合规的分支
git branch -a | sed 's/^[* ]*//' | grep -v -E '^(main|develop|feature/[a-z0-9-]+|hotfix/[a-z0-9-]+|release/v[0-9]+\.[0-9]+\.[0-9]+|remotes/origin/(main|develop|feature/[a-z0-9-]+|hotfix/[a-z0-9-]+|release/v[0-9]+\.[0-9]+\.[0-9]+))$'
```

### A.2 文档更新时间戳检查命令

#### 检查文档最后更新时间
```bash
# 检查所有 Markdown 文档的最后修改时间
find . -name "*.md" -type f ! -path "./node_modules/*" ! -path "./.git/*" -exec stat -c "%Y %n" {} \; | sort -rn | head -20

# 检查超过90天未更新的文档
find . -name "*.md" -type f ! -path "./node_modules/*" ! -path "./.git/*" -mtime +90 -exec ls -lh {} \;
```

#### 检查文档时间戳与 Git 提交一致性
```bash
# 检查文档修改时间与 Git 提交时间差异
check_doc_timestamp() {
  local doc="$1"
  local file_time=$(stat -c %Y "$doc" 2>/dev/null || stat -f %m "$doc" 2>/dev/null)
  local git_time=$(git log -1 --format=%at -- "$doc" 2>/dev/null)
  
  if [ -n "$git_time" ] && [ -n "$file_time" ]; then
    local diff=$(($file_time - $git_time))
    [ ${diff#-} -gt 60 ] && echo "时间不一致: $doc (差异 ${diff}秒)"
  fi
}

# 遍历检查所有文档
for doc in $(find . -name "*.md" -type f ! -path "./node_modules/*" ! -path "./.git/*"); do
  check_doc_timestamp "$doc"
done
```

#### 检查关键文档列表
```bash
# 列出关键文档及其状态
echo "=== 角色 IDENTITY 文档 ==="
for agent in zhangliang xiaohe hanxin chenping zhoubo caocan lishiyi lujia shusuntong xiahouying; do
  file="agents/$agent/IDENTITY.md"
  if [ -f "$file" ]; then
    mtime=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
    echo "✅ $agent: $mtime"
  else
    echo "❌ $agent: 文件缺失"
  fi
done

echo ""
echo "=== 工作流程文档 ==="
for workflow in external_assistant_workflow.md personal_assistant_workflow.md internal_delivery_workflow.md; do
  file="workflows/$workflow"
  if [ -f "$file" ]; then
    mtime=$(stat -c %y "$file" 2>/dev/null | cut -d' ' -f1)
    echo "✅ $workflow: $mtime"
  else
    echo "❌ $workflow: 文件缺失"
  fi
done
```

### A.3 角色文件完整性检查命令

#### 检查所有必需 Agent 的 IDENTITY 文件
```bash
#!/bin/bash
# check_agents.sh - 快速检查 Agent 文件完整性

REQUIRED_AGENTS=(
  "zhangliang:张良(产品经理)"
  "xiaohe:萧何(架构师)"
  "hanxin:韩信(全栈研发)"
  "chenping:陈平(测试工程师)"
  "zhoubo:周勃(运维工程师)"
  "caocan:曹参(PMO)"
  "lishiyi:郦食其(外部助理)"
  "lujia:陆贾(知识库管理员)"
  "shusuntong:叔孙通(设计师)"
  "xiahouying:夏侯婴(私人助理)"
)

MISSING=0
INCOMPLETE=0

echo "=== Agent IDENTITY 文件检查 ==="
for agent_info in "${REQUIRED_AGENTS[@]}"; do
  agent_id="${agent_info%%:*}"
  agent_name="${agent_info##*:}"
  identity_file="agents/$agent_id/IDENTITY.md"
  
  if [ ! -f "$identity_file" ]; then
    echo "❌ 缺失: $agent_name ($identity_file)"
    ((MISSING++))
  else
    # 检查必需内容
    content=$(cat "$identity_file" 2>/dev/null)
    
    # 检查关键字段
    has_all=true
    for keyword in "模型配置" "官方职位" "核心权责"; do
      if ! echo "$content" | grep -q "$keyword"; then
        echo "⚠️  $agent_name: 缺少 '$keyword'"
        has_all=false
      fi
    done
    
    if [ "$has_all" = true ]; then
      echo "✅ $agent_name"
    else
      ((INCOMPLETE++))
    fi
  fi
done

echo ""
echo "统计: 缺失=$MISSING 不完整=$INCOMPLETE"
[ "$MISSING" -eq 0 ] && [ "$INCOMPLETE" -eq 0 ] && echo "✅ 所有 Agent 文件完整"
```

#### 检查工作流程文档完整性
```bash
#!/bin/bash
# check_workflows.sh - 检查工作流程文档

REQUIRED_WORKFLOWS=(
  "external_assistant_workflow.md:外部助理流程"
  "personal_assistant_workflow.md:私人助理流程"
  "internal_delivery_workflow.md:交付闭环流程"
)

echo "=== 工作流程文档检查 ==="
for wf_info in "${REQUIRED_WORKFLOWS[@]}"; do
  filename="${wf_info%%:*}"
  name="${wf_info##*:}"
  filepath="workflows/$filename"
  
  if [ ! -f "$filepath" ]; then
    echo "❌ 缺失: $name"
  else
    # 检查章节完整性
    content=$(cat "$filepath")
    has_overview=$(echo "$content" | grep -c "流程概述")
    has_steps=$(echo "$content" | grep -c "执行步骤")
    
    if [ "$has_overview" -gt 0 ] && [ "$has_steps" -gt 0 ]; then
      echo "✅ $name"
    else
      echo "⚠️  $name: 章节不完整"
    fi
  fi
done
```

### A.4 一键执行命令

#### 快速执行所有检查
```bash
# 使用本脚本执行完整检查
cd InfinityCompany
./scripts/traceability_check.sh

# 仅执行 Git 检查
./scripts/traceability_check.sh git

# 仅执行文档检查
./scripts/traceability_check.sh docs

# 仅执行 Agent 检查
./scripts/traceability_check.sh agents

# 指定时间范围
./scripts/traceability_check.sh all --since "3 days ago"
```

#### CI/CD 集成命令
```bash
# GitHub Actions / GitLab CI 中使用
./scripts/traceability_check.sh all --since "1 day ago" || exit 1
```

---

## 附录 B：角色职责速查表

### B.1 各角色检查职责

| 角色 | 主要职责 | 检查频率 | 检查内容 |
|-----|---------|---------|---------|
| **周勃** | 运维检查 | 每日 18:00 | 环境检查、脚本执行、报告生成 |
| **曹参** | PMO 检查 | 每日 | 复盘及时性、Notion 看板、改进项跟进 |
| **陆贾** | 知识库检查 | 每日 | 文档完整性、模板合规、版本关联 |
| **萧何** | 架构检查 | 每次提交 | 代码提交规范、分支策略、技术文档 |
| **韩信** | 研发自查 | 每次提交 | 代码提交信息、Task 状态、工时记录 |
| **陈平** | 测试检查 | 每日 | Bug 记录完整性、修复说明、验证记录 |
| **张良** | 产品审查 | 每周 | 需求关联、Story 规范、PRD 版本 |
| **夏侯婴** | 助理分发 | 实时 | 异常告警分发、跟踪处理进度 |

### B.2 检查频率对照表

| 检查项 | 频率 | 触发方式 | 执行者 |
|-------|-----|---------|-------|
| 提交信息格式 | 实时 | Git Hook | 自动 |
| 分支命名规范 | 每日 | 脚本检查 | 周勃 |
| 文档时间戳 | 每日 | 脚本检查 | 自动 |
| Agent 文件完整性 | 每日 | 脚本检查 | 自动 |
| Notion 必填字段 | 每日 | Notion API | 自动 |
| 复盘及时性 | 每日 | Notion API | 自动 |
| 改进项跟进 | 每周 | 脚本检查 | 曹参 |
| 合规报告审查 | 每周 | 手动 | 张良 |

---

**文档版本**: v1.1  
**最后更新**: 2026-03-28  
**维护者**: 陆贾(知识库管理员) / 周勃(运维工程师)
