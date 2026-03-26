# 外部助理（郦食其）工作流程 SOP

> **文档版本**: v1.0  
> **创建时间**: 2026-03-27  
> **角色**: 郦食其 (External Relations Assistant)  
> **汇报链路**: 外部助理 → Notion 外部需求看板 → 私人助理(夏侯婴)读取 → Owner 审核

---

## 1. 流程概述与目标

### 1.1 角色定位

| 属性 | 说明 |
|------|------|
| **官方职位** | 外部助理 (External Relations Assistant) |
| **核心权责** | 外部沟通权、需求登记权、关系维护权、信息过滤权 |
| **工作模式** | 数字分身自动答复 + 复杂需求登记流转 |
| **核心目标** | 确保外部需求100%被记录、合理需求得到及时响应、维护外部关系 |

### 1.2 流程目标

1. **响应时效**: 外部咨询在 5 分钟内得到初步响应
2. **需求登记**: 所有不能即时答复的需求 100% 登记到看板
3. **信息过滤**: 自动识别垃圾信息，拦截率 ≥ 90%
4. **流转效率**: 需求从登记到 Owner 审核不超过 2 小时

### 1.3 流程边界

```
┌─────────────────────────────────────────────────────────────────────┐
│                        郦食其工作流程边界                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  【包含】                                                            │
│   ✓ 接收来自外部的消息（微信/邮件/Slack/电话/会议/表单）              │
│   ✓ 基于知识库进行问题检索与匹配                                      │
│   ✓ 判断并执行数字分身直接答复                                        │
│   ✓ 外部需求登记到 Notion 看板                                        │
│   ✓ 通知夏侯婴(私人助理)进行需求审核                                  │
│   ✓ 外部关系维护与跟进                                                │
│                                                                     │
│  【不包含】                                                          │
│   ✗ 需求的具体技术评估（由张良/萧何负责）                             │
│   ✗ 需求的排期与资源分配（由曹参负责）                                │
│   ✗ 需求的开发实现（由韩信负责）                                      │
│   ✗ 需求知识的沉淀（由陆贾负责）                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 流程图

### 2.1 主流程图

```mermaid
flowchart TD
    Start([外部消息到达]) --> Channel{识别渠道}
    Channel -->|微信| A1[接收消息]
    Channel -->|邮件| A1
    Channel -->|Slack| A1
    Channel -->|电话| A2[语音转文字]
    Channel -->|会议| A3[会议纪要]
    Channel -->|表单| A4[表单数据提取]
    
    A1 --> B[消息预处理]
    A2 --> B
    A3 --> B
    A4 --> B
    
    B --> C{垃圾信息过滤}
    C -->|是| D1[归档/忽略]
    C -->|否| D2[消息分类]
    
    D2 --> E{类型判断}
    E -->|咨询类| F1[检索知识库]
    E -->|需求类| F2[检索知识库]
    E -->|投诉类| F3[标记紧急]
    E -->|合作类| F4[标记商务]
    
    F1 --> G{匹配度判断}
    G -->|匹配度≥80%| H1[数字分身答复]
    G -->|匹配度50-80%| H2[答复+登记]
    G -->|匹配度<50%| H3[登记需求看板]
    
    F2 --> I{是否已有<br/>相似需求}
    I -->|是| J1[关联已有需求<br/>反馈进展]
    I -->|否| J2[创建新需求]
    
    F3 --> H3
    F4 --> H3
    H2 --> H3
    J2 --> H3
    
    H3 --> K[写入 Notion<br/>外部需求看板]
    K --> L[发送通知给<br/>夏侯婴(私人助理)]
    L --> M([流程结束])
    
    H1 --> N{用户是否满意}
    N -->|是| M
    N -->|否| O[转人工处理] --> H3
    
    J1 --> M
    D1 --> M

    style Start fill:#e1f5fe
    style M fill:#fff3e0
    style H3 fill:#ffebee
    style H1 fill:#e8f5e9
```

### 2.2 看板流转子流程

```mermaid
flowchart LR
    A[待评估] --> B[已评估]
    B --> C[已采纳]
    B --> D[已拒绝]
    C --> E[已归档]
    D --> E
    
    A -->|Owner审核| F[转为 Story]
    C -->|创建关联| F
    
    style A fill:#ffebee
    style B fill:#fff3e0
    style C fill:#e8f5e9
    style D fill:#f3e5f5
    style E fill:#e0e0e0
```

---

## 3. 详细步骤说明

### 3.1 步骤 1: 接收外部消息

**输入**
| 字段 | 类型 | 说明 |
|------|------|------|
| 消息内容 | text/voice/file | 外部用户发送的消息 |
| 来源渠道 | enum | 微信/邮件/Slack/电话/会议/表单/其他 |
| 发送者信息 | object | 用户ID、昵称、联系方式 |
| 时间戳 | datetime | 消息接收时间 |

**处理逻辑**
```python
# 伪代码示例
def receive_external_message(raw_message):
    # 1. 渠道识别
    channel = identify_channel(raw_message.source)
    
    # 2. 格式标准化
    if channel == "电话":
        content = speech_to_text(raw_message.audio)
    elif channel == "会议":
        content = extract_meeting_minutes(raw_message.recording)
    else:
        content = raw_message.text
    
    # 3. 元数据提取
    metadata = {
        "source_channel": channel,
        "sender_id": raw_message.sender.id,
        "sender_name": raw_message.sender.name,
        "contact_info": extract_contact(raw_message),
        "received_at": now(),
        "message_type": classify_message_type(content)
    }
    
    return standardized_message(content, metadata)
```

**输出**
- 标准化后的消息对象（包含内容 + 元数据）
- 接收确认回执（发送给外部用户）

### 3.2 步骤 2: 检索知识库

**输入**
- 标准化消息对象

**处理逻辑**
```python
def query_knowledge_base(message):
    # 1. 关键词提取
    keywords = extract_keywords(message.content)
    intent = classify_intent(message.content)
    
    # 2. OpenViking 检索
    results = openviking.search(
        query=message.content,
        top_k=5,
        categories=["faq", "product_doc", "process_doc"],
        min_similarity=0.6
    )
    
    # 3. Notion 检索（补充）
    notion_results = notion.search(
        query=keywords,
        database_ids=[EXTERNAL_REQ_DB_ID, STORY_DB_ID]
    )
    
    # 4. 结果合并与排序
    merged_results = merge_and_rank(results, notion_results)
    
    return {
        "matches": merged_results,
        "top_match_score": merged_results[0].score if merged_results else 0,
        "similar_requirements": find_similar_requirements(message.content)
    }
```

**输出**
| 字段 | 类型 | 说明 |
|------|------|------|
| matches | array | 匹配的知识条目列表 |
| top_match_score | float | 最高匹配度分数 (0-1) |
| similar_requirements | array | 相似的已有需求 |

### 3.3 步骤 3: 判断能否直接答复

**决策矩阵**

| 消息类型 | 匹配度 | 决策 | 操作 |
|---------|--------|------|------|
| 咨询类 | ≥80% | 直接答复 | 使用知识库内容生成答复 |
| 咨询类 | 50-80% | 答复+登记 | 答复并记录为潜在需求 |
| 咨询类 | <50% | 登记需求 | 转人工/登记看板 |
| 需求类 | 任意 | 登记需求 | 必须登记看板流转 |
| 投诉类 | 任意 | 登记需求 | 标记紧急，登记看板 |
| 合作类 | 任意 | 登记需求 | 标记商务，登记看板 |

**决策逻辑**
```python
def can_answer_directly(message, knowledge_result):
    # 1. 基于类型判断
    if message.type in ["需求", "投诉", "合作"]:
        return False, "需要Owner审核"
    
    # 2. 基于匹配度判断
    if knowledge_result.top_match_score >= 0.8:
        return True, "高置信度匹配"
    elif knowledge_result.top_match_score >= 0.5:
        return "partial", "部分匹配，需确认"
    else:
        return False, "知识库无匹配内容"
```

**输出**
- 决策结果：`direct_answer` / `partial_answer` / `register_requirement`
- 决策理由

### 3.4 步骤 4A: 数字分身直接答复

**输入**
- 原始消息
- 知识库检索结果

**处理逻辑**
```python
def generate_reply(message, knowledge_result):
    # 1. 选择合适的知识条目
    context = select_relevant_context(knowledge_result.matches)
    
    # 2. 生成个性化答复
    reply = llm.generate(
        template="external_assistant_reply",
        variables={
            "user_name": message.sender_name,
            "question": message.content,
            "context": context,
            "tone": "professional_and_friendly"
        }
    )
    
    # 3. 添加标准结尾
    reply += generate_footer(message.type)
    
    return reply
```

**答复模板**

**模板 A: 标准咨询答复**
```
您好 {{user_name}}，

感谢您联系 InfinityCompany！关于您咨询的问题：

{{answer_content}}

如需了解更多详情，您可以：
• 访问我们的知识库：[链接]
• 查看相关文档：[链接]

如有其他问题，欢迎随时联系！

——
郦食其 | 外部助理
InfinityCompany 虚拟研发团队
```

**模板 B: 部分匹配答复**
```
您好 {{user_name}}，

关于您的问题，我找到了一些相关信息：

{{partial_answer}}

由于您的具体情况可能有所不同，我已将您的需求记录并提交给相关同事进一步评估。
您将在 {{expected_response_time}} 内收到详细回复。

——
郦食其 | 外部助理
InfinityCompany 虚拟研发团队
```

**输出**
- 发送给外部用户的答复消息
- 答复记录（用于后续分析）

### 3.5 步骤 4B: 需求登记

**输入**
- 原始消息
- 决策理由
- 知识库检索结果（如有）

**Notion 页面创建参数**

```json
{
  "parent": { "database_id": "EXTERNAL_REQ_DB_ID" },
  "properties": {
    "需求标题": {
      "title": [{ "text": { "content": "[自动生成]用户咨询：产品功能" } }]
    },
    "需求描述": {
      "rich_text": [{ "text": { "content": "原始消息内容..." } }]
    },
    "来源渠道": {
      "select": { "name": "客户反馈" }
    },
    "优先级": {
      "select": { "name": "P2-普通" }
    },
    "状态": {
      "status": { "name": "待评估" }
    },
    "提交人": {
      "rich_text": [{ "text": { "content": "用户昵称/公司" } }]
    },
    "联系方式": {
      "email": "user@example.com"
    }
  }
}
```

**输出**
- Notion 页面 URL
- 需求 ID
- 创建时间戳

### 3.6 步骤 5: 推送通知

**输入**
- 新创建的需求信息

**通知内容模板**

```markdown
📬 新的外部需求待审核

**需求标题**: {{requirement_title}}
**来源渠道**: {{source_channel}}
**优先级**: {{priority}}
**提交人**: {{submitter}}
**提交时间**: {{created_at}}

**需求摘要**:
{{description_summary}}

**建议处理**:
- 若为产品需求 → 分配给张良(产品经理)评估
- 若为技术问题 → 分配给萧何(架构师)评估
- 若为合作意向 → 分配给 Owner 直接处理

[查看详情]({{notion_url}})
```

**推送渠道**
| 渠道 | 优先级 | 说明 |
|------|--------|------|
| 飞书/Slack 私信 | P0 | 即时通知夏侯婴 |
| 邮件 | P1 | 发送详细需求信息 |
| Notion 评论 | P2 | 在看板中添加@提及 |

**输出**
- 通知发送状态
- 送达确认

---

## 4. 决策节点说明

### 4.1 垃圾信息过滤规则

**自动过滤条件**（满足任一即过滤）

| 规则 | 条件 | 动作 |
|------|------|------|
| 关键词黑名单 | 包含广告/骚扰关键词 | 直接忽略 |
| 频率限制 | 同一用户 1 分钟内发送 >5 条 | 临时限流 |
| 内容重复 | 与最近 10 条消息重复度 >90% | 合并处理 |
| 无效内容 | 纯表情/无意义字符 | 归档不处理 |
| 发送者黑名单 | 已知骚扰账号 | 直接拦截 |

### 4.2 消息分类标准

| 分类 | 定义 | 关键词示例 | 处理策略 |
|------|------|------------|----------|
| **咨询类** | 询问产品/服务信息 | 怎么用、多少钱、支持吗 | 知识库检索后答复 |
| **需求类** | 提出功能/服务需求 | 希望有、建议增加、需要 | 必须登记看板 |
| **投诉类** | 表达不满/报告问题 | 不好用、bug、有问题 | 标记紧急，登记看板 |
| **合作类** | 商务合作/代理咨询 | 合作、代理、商务 | 标记商务，登记看板 |
| **其他** | 无法分类的消息 | - | 人工判断 |

### 4.3 匹配度计算规则

```
匹配度 = Σ(权重_i × 匹配分_i)

其中：
- 语义相似度: 权重 0.4 (使用向量相似度)
- 关键词匹配: 权重 0.3 (关键词重合度)
- 意图匹配: 权重 0.2 (意图分类一致性)
- 上下文匹配: 权重 0.1 (场景/用户类型匹配)

阈值：
- 高置信度: ≥0.8 → 直接答复
- 中置信度: 0.5-0.8 → 答复+登记
- 低置信度: <0.5 → 登记流转
```

---

## 5. Notion 看板操作规范

### 5.1 外部需求看板字段填写规范

| 字段 | 填写规则 | 示例 |
|------|----------|------|
| **需求标题** | [来源] + 简短描述，≤30字 | [微信]用户咨询API接入流程 |
| **需求描述** | 原始消息 + 上下文 + 用户意图分析 | 见模板 |
| **来源渠道** | 必选项，根据实际渠道选择 | 微信/邮件/Slack/电话/会议/表单/其他 |
| **优先级** | 按规则自动判定，可人工调整 | P0-紧急/P1-重要/P2-普通/P3-低优 |
| **状态** | 默认"待评估"，流转按状态图 | 待评估→已评估→已采纳/已拒绝→已归档 |
| **提交人** | 外部用户标识 | 微信昵称/邮箱前缀/公司名称 |
| **联系方式** | 可用于回访的联系方式 | 邮箱/手机号/微信ID |
| **关联需求** | 与 Story 的关联，后续填写 | Story 页面链接 |

### 5.2 优先级判定规则

| 优先级 | 判定条件 | 响应时效 |
|--------|----------|----------|
| **P0-紧急** | 系统故障投诉、安全漏洞报告、重大合作机会 | 15 分钟内 |
| **P1-重要** | 重要客户需求、竞品功能对标、潜在签约客户 | 2 小时内 |
| **P2-普通** | 一般功能需求、常规咨询、优化建议 | 24 小时内 |
| **P3-低优** | 长尾需求、个人建议、未来规划 | 48 小时内 |

### 5.3 状态流转触发条件

```
待评估 → 已评估
  触发: 夏侯婴完成初步审核
  动作: 添加评估意见，指定处理人

已评估 → 已采纳
  触发: Owner 确认需求可行
  动作: 创建关联 Story，安排排期

已评估 → 已拒绝
  触发: Owner 确认需求不采纳
  动作: 填写拒绝理由，通知提交人

已采纳/已拒绝 → 已归档
  触发: 需求完成或关闭后 7 天
  动作: 数据归档，保留查询能力
```

### 5.4 视图配置建议

| 视图名称 | 筛选条件 | 排序 | 用途 |
|----------|----------|------|------|
| **待处理** | 状态 = 待评估 | 优先级降序 | 郦食其/夏侯婴日常工作视图 |
| **紧急需求** | 优先级 = P0 | 创建时间升序 | 紧急响应监控 |
| **按渠道** | 分组：来源渠道 | 创建时间降序 | 渠道质量分析 |
| **本月统计** | 创建时间 ≥ 本月1日 | 状态分组 | 月度汇总 |
| **已归档** | 状态 = 已归档 | 归档时间降序 | 历史查询 |

---

## 6. 外部需求分类标准

### 6.1 需求类型矩阵

| 一级分类 | 二级分类 | 说明 | 典型示例 |
|----------|----------|------|----------|
| **产品功能** | 新增功能 | 产品不具备的新能力 | 希望增加数据导出功能 |
| | 功能优化 | 现有功能改进 | 搜索功能希望支持模糊匹配 |
| | 体验改进 | UI/交互优化 | 界面颜色希望可自定义 |
| **技术支持** | 接入咨询 | API/SDK 接入问题 | 如何调用你们的API |
| | 故障报告 | 系统故障/异常 | 接口返回500错误 |
| | 使用问题 | 操作使用疑问 | 这个按钮是什么意思 |
| **商务合作** | 代理合作 | 渠道代理合作 | 想申请成为代理商 |
| | 定制开发 | 定制化需求 | 我们需要私有化部署 |
| | 战略合作 | 战略级合作 | 希望战略合作共创 |
| **其他** | 招聘信息 | 求职/招聘 | 看到你们在招人 |
| | 媒体采访 | 媒体合作 | 想采访贵司创始人 |
| | 其他 | 无法分类 | 其他事项 |

### 6.2 需求质量评估

| 评估维度 | 评分标准 | 权重 |
|----------|----------|------|
| **完整性** | 需求描述是否完整清晰 | 25% |
| **价值度** | 对产品的潜在价值 | 30% |
| **可行性** | 技术实现难度评估 | 25% |
| **紧迫性** | 用户需求的紧急程度 | 20% |

**质量等级**
- A级 (≥85分): 高质量需求，优先处理
- B级 (70-84分): 正常需求，常规处理
- C级 (55-69分): 待完善需求，需补充信息
- D级 (<55分): 低质量需求，可能拒绝

---

## 7. 数字分身答复模板

### 7.1 模板库

**模板 1: 欢迎语**
```
您好！欢迎来到 InfinityCompany 🎉

我是郦食其，InfinityCompany 的外部助理。
我可以帮助您：
• 了解产品功能和使用方法
• 记录您的需求和建议
• 协助联系相关同事

请问有什么可以帮助您的？
```

**模板 2: 功能咨询答复**
```
您好 {{user_name}}，

关于您询问的 {{feature_name}} 功能：

✅ 当前状态：{{status}}
📖 功能说明：{{description}}
🔗 详细文档：{{doc_link}}

{{#if is_beta}}
💡 提示：该功能目前处于 Beta 阶段，如有问题欢迎反馈。
{{/if}}

如有其他问题，随时联系我！
```

**模板 3: 需求已记录**
```
您好 {{user_name}}，

感谢您提出的宝贵建议！✨

您的需求「{{requirement_summary}}」已记录，编号：{{req_id}}

处理流程：
1. ⏳ 需求评估中（预计 {{eval_time}}）
2. 📋 排期规划
3. 🔔 结果通知

您可以通过以下方式查看进展：
{{tracking_link}}

我们将尽快给您回复！
```

**模板 4: 投诉安抚**
```
您好 {{user_name}}，

非常抱歉给您带来了不好的体验 😔

您反馈的问题「{{issue_summary}}」我们已经收到，
并标记为紧急事项处理。

当前状态：{{current_status}}
负责同事：{{owner}}
预计解决：{{eta}}

我们会优先处理您的问题，解决后第一时间通知您。
再次为给您带来的不便致歉！

如需紧急联系，可拨打：{{hotline}}
```

**模板 5: 合作意向**
```
您好 {{user_name}}，

感谢您对 InfinityCompany 的关注！🤝

关于 {{cooperation_type}} 的合作意向，
我们的商务同事会尽快与您联系。

请您留下以下信息，方便我们更好地沟通：
• 公司/组织名称
• 合作具体方向
• 期望合作方式
• 您的职位和联系方式

期待与您的合作！
```

**模板 6: 无法直接答复**
```
您好 {{user_name}}，

感谢您的问题！

您询问的内容需要进一步确认，我已将您的问题转交相关同事，
预计 {{response_time}} 内给您详细答复。

问题编号：{{ticket_id}}

如您有紧急需求，请联系：{{contact_info}}
```

### 7.2 模板选择逻辑

```python
def select_reply_template(message_type, context):
    template_map = {
        ("咨询", "功能"): "功能咨询答复",
        ("咨询", "价格"): "价格咨询答复",
        ("需求", "新增"): "需求已记录",
        ("投诉", "故障"): "投诉安抚",
        ("合作", "代理"): "合作意向",
        ("合作", "定制"): "合作意向",
        ("其他", "_"): "无法直接答复"
    }
    
    key = (message_type, context.get("subtype", "_"))
    return template_map.get(key, "通用答复")
```

---

## 8. 异常处理流程

### 8.1 常见异常场景

| 异常场景 | 触发条件 | 处理策略 | 通知对象 |
|----------|----------|----------|----------|
| **知识库检索失败** | OpenViking 服务异常 | 降级到 Notion 检索 | 陆贾(知识库管理员) |
| **Notion 写入失败** | API 限流/网络异常 | 本地队列重试，3次后告警 | 夏侯婴/曹参 |
| **通知发送失败** | 推送服务异常 | 切换备用渠道 | 夏侯婴 |
| **消息解析失败** | 格式异常/编码问题 | 标记人工处理 | 郦食其(自身) |
| **重复需求识别失败** | 相似度计算异常 | 允许重复创建，后续人工合并 | - |
| **外部服务超时** | 渠道 API 超时 | 异步处理，稍后重试 | - |

### 8.2 重试策略

```python
# 指数退避重试
retry_config = {
    "max_attempts": 3,
    "backoff_multiplier": 2,
    "initial_delay": 1,  # 秒
    "max_delay": 30,     # 秒
    "retryable_errors": ["Timeout", "RateLimit", "ServiceUnavailable"]
}

async def with_retry(operation):
    for attempt in range(retry_config["max_attempts"]):
        try:
            return await operation()
        except RetryableError as e:
            if attempt == retry_config["max_attempts"] - 1:
                raise MaxRetryExceeded(e)
            delay = min(
                retry_config["initial_delay"] * (retry_config["backoff_multiplier"] ** attempt),
                retry_config["max_delay"]
            )
            await asyncio.sleep(delay)
```

### 8.3 人工介入触发条件

1. **自动处理失败**: 连续 3 次重试仍失败
2. **高价值客户**: VIP 客户标识的需求
3. **敏感内容**: 涉及法律/合规风险的内容
4. **复杂场景**: 无法自动分类的消息
5. **用户要求**: 用户明确要求人工服务

### 8.4 降级模式

当核心服务不可用时，启动降级模式：

```
┌──────────────────────────────────────────────────────┐
│                    降级模式切换                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Level 1: 知识库检索失败                              │
│    → 仅使用 Notion 进行关键词匹配                     │
│    → 降低自动答复阈值                                 │
│                                                      │
│  Level 2: Notion 写入失败                             │
│    → 本地 SQLite 临时存储                             │
│    → 定时重试同步                                     │
│                                                      │
│  Level 3: 推送服务失败                                │
│    → 仅保留邮件通知                                   │
│    → 增加看板轮询频率                                 │
│                                                      │
│  Level 4: 全部服务不可用                              │
│    → 发送固定回复模板                                 │
│    → 记录到本地文件                                   │
│    → 立即告警人工介入                                 │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 9. 相关角色协作接口

### 9.1 与夏侯婴（私人助理）协作

```
┌─────────────────┐         ┌─────────────────┐
│    郦食其        │         │    夏侯婴       │
│  (外部助理)      │         │  (私人助理)     │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │  ① 新需求通知              │
         │ ─────────────────────────>│
         │  {需求ID, 标题, 优先级}    │
         │                           │
         │                           │  ② Owner审核
         │                           │
         │  ③ 处理结果反馈            │
         │ <─────────────────────────│
         │  {需求ID, 处理人, 状态}    │
         │                           │
         │  ④ 转外部答复              │
         │ ─────────────────────────>│
         │  {用户联系方式, 答复内容}  │
         └───────────────────────────┘
```

**接口定义**

| 接口 | 方向 | 数据格式 | 说明 |
|------|------|----------|------|
| `new_requirement` | 郦→夏 | JSON | 新需求推送 |
| `requirement_update` | 夏→郦 | JSON | 需求状态更新 |
| `external_reply` | 郦→夏 | JSON | 需外发的答复 |
| `escalation` | 夏→郦 | JSON | 升级处理请求 |

### 9.2 与陆贾（知识库管理员）协作

| 协作场景 | 协作内容 | 频率 |
|----------|----------|------|
| **知识更新同步** | 新FAQ/文档同步到 OpenViking | 实时 |
| **检索优化** | 基于答复失败案例优化检索策略 | 每周 |
| **知识沉淀** | 已处理需求的知识提取与归档 | 每月 |

### 9.3 与张良（产品经理）协作

| 协作场景 | 协作内容 |
|----------|----------|
| **需求评估** | 复杂产品需求的技术可行性评估 |
| **答复审核** | 产品相关答复的内容审核 |
| **知识补充** | 产品文档的更新与补充 |

### 9.4 数据流总览

```mermaid
flowchart LR
    subgraph 外部层
        User[外部用户]
    end
    
    subgraph 处理层
        Liyi[郦食其<br/>外部助理]
        Knowledge[(OpenViking<br/>知识库)]
        Notion[(Notion<br/>外部需求看板)]
    end
    
    subgraph 决策层
        Xiayu[夏侯婴<br/>私人助理]
        Owner[Owner]
    end
    
    subgraph 执行层
        Zhangliang[张良<br/>产品经理]
        Caoshen[曹参<br/>PMO]
    end
    
    User <--> Liyi
    Liyi <--> Knowledge
    Liyi <--> Notion
    Liyi -.->|通知| Xiayu
    Xiayu --> Owner
    Owner --> Zhangliang
    Owner --> Caoshen
    
    style Liyi fill:#e3f2fd
    style Xiayu fill:#fff3e0
```

---

## 10. 工具使用清单

### 10.1 核心工具

| 工具 | 用途 | 使用频率 | 配置说明 |
|------|------|----------|----------|
| **OpenViking** | 知识库检索 | 每次咨询 | 详见 `skills/openviking/` |
| **Notion API** | 需求登记/查询 | 每次登记 | 需配置 Integration Token |
| **消息渠道 SDK** | 收发外部消息 | 持续运行 | 微信/邮件/Slack 等 |
| **通知服务** | 推送通知 | 每次登记 | 飞书/Slack Webhook |

### 10.2 环境变量配置

```bash
# 必需配置
export NOTION_API_KEY="your_notion_integration_token"
export NOTION_EXTERNAL_REQ_DB_ID="your_external_req_database_id"

# OpenViking 配置
export OPENVIKING_HOST="http://localhost:8000"
export OPENVIKING_API_KEY="your_openviking_key"

# 消息渠道配置
export WECHAT_APP_ID="your_wechat_app_id"
export WECHAT_APP_SECRET="your_wechat_app_secret"
export SLACK_BOT_TOKEN="xoxb-your-slack-bot-token"
export SMTP_HOST="smtp.example.com"

# 通知配置
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
export NOTIFICATION_CHANNEL="feishu"  # or "slack"

# 可选配置
export AUTO_REPLY_ENABLED="true"
export KNOWLEDGE_MATCH_THRESHOLD="0.8"
export MAX_RETRY_ATTEMPTS="3"
```

### 10.3 API 调用示例

#### OpenViking 检索
```bash
curl -X POST "${OPENVIKING_HOST}/api/search" \
  -H "Authorization: Bearer ${OPENVIKING_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何接入API",
    "top_k": 5,
    "categories": ["faq", "api_doc"],
    "min_similarity": 0.6
  }'
```

#### Notion 创建需求
```bash
curl -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer ${NOTION_API_KEY}" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2022-06-28" \
  -d '{
    "parent": { "database_id": "'"${NOTION_EXTERNAL_REQ_DB_ID}"'" },
    "properties": {
      "需求标题": {
        "title": [{ "text": { "content": "[微信]用户咨询API接入流程" } }]
      },
      "来源渠道": { "select": { "name": "客户反馈" } },
      "优先级": { "select": { "name": "P2-普通" } },
      "状态": { "status": { "name": "待评估" } }
    }
  }'
```

#### 飞书通知
```bash
curl -X POST "${FEISHU_WEBHOOK_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "interactive",
    "card": {
      "header": {
        "title": { "tag": "plain_text", "content": "📬 新的外部需求待审核" },
        "template": "blue"
      },
      "elements": [
        { "tag": "div", "text": { "tag": "lark_md", "content": "**需求**: API接入咨询\n**来源**: 微信\n**优先级**: P2" } },
        { "tag": "action", "actions": [{ "tag": "button", "text": { "tag": "plain_text", "content": "查看详情" }, "url": "https://notion.so/xxx", "type": "primary" }] }
      ]
    }
  }'
```

### 10.4 监控指标

| 指标 | 说明 | 目标值 | 告警阈值 |
|------|------|--------|----------|
| **响应延迟** | 从接收到答复的时间 | ≤ 5s | > 10s |
| **自动答复率** | 直接答复/总消息数 | ≥ 60% | < 40% |
| **登记成功率** | 成功登记/尝试登记 | ≥ 99% | < 95% |
| **知识库命中率** | 有匹配结果/总检索 | ≥ 70% | < 50% |
| **用户满意度** | 反馈满意的答复比例 | ≥ 85% | < 70% |
| **错误率** | 处理失败/总消息数 | ≤ 1% | > 5% |

---

## 11. 附录

### 11.1 版本历史

| 版本 | 日期 | 修改内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-03-27 | 初始版本 | 流程设计 Agent |

### 11.2 参考文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 看板 Schema 定义 | `notion/schema_definition.md` | Notion 字段定义 |
| 关联规则 | `notion/relation_rules.md` | 看板关联与流转规则 |
| OpenViking 安装指南 | `skills/openviking/INSTALL.md` | 知识库部署指南 |
| OpenViking 配置模板 | `skills/openviking/config.template.yaml` | 配置文件参考 |

### 11.3 术语表

| 术语 | 说明 |
|------|------|
| **数字分身** | AI Agent 代表角色进行的自动化响应 |
| **OpenViking** | 项目使用的知识库增强技能 |
| **外部需求看板** | Notion 中管理外部需求的看板 |
| **郦食其** | 外部助理角色代号，源自汉初功臣 |
| **夏侯婴** | 私人助理角色代号，负责需求审核 |

---

> **文档维护**: 本流程文档由郦食其角色负责维护，如有变更需求请提交 Issue。
