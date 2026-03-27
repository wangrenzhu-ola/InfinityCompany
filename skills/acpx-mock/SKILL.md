# acpx-mock Skill

acpx 插件的 Fallback 实现，当真实的 acpx 插件不可用时，使用 CLI 方式模拟实时通讯。

## 功能

- 模拟 `acpx <agent_id> "message"` 命令
- 通过 company-directory 的 email 功能发送消息
- 使用 response_required 消息类型确保对方知晓

## 使用

```bash
# 发送实时消息（模拟）
acpx-mock hanxin "请检查这个问题"

# 或通过 company-directory 集成
company-directory acpx hanxin "请检查这个问题"
```
