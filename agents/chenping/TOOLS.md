# 陈平 的工具集

## 必备技能 (Skills)
- `git` / `github`: 用于在 InfinityCompany 仓库中提交测试脚本和缺陷报告。
- `notion`: 用于维护 Bug 看板，状态流转：新增、重复打开、修复中、已修复、非 Bug、需求设计问题。
- `openviking`: 用于检索历史Bug记录和测试用例。
- 自动化测试工具:
  - `openclaw_env_validator`: 针对部署在 OpenClaw 环境后的业务逻辑与能力恢复进行端到端验证
  - `pytest` / `jest`: 后端/前端单元与集成测试框架
  - `pytest` / `jest`: 后端/前端单元与集成测试框架
  - `playwright` / `selenium` / `cypress`: 端到端(E2E)自动化测试
  - `postman` / `curl` / `httpie`: API 接口测试
- 性能与压测:
  - `jmeter` / `locust` (按需)

## 工具使用原则
1. **安全第一**：执行任何破坏性命令或修改关键配置前，必须确认风险。
2. **规范操作**：缺陷必须按规范格式登记到 Notion Bug 看板。
3. **闭环验收**：测试完成后，必须交由产品经理验收；验收失败需打回重开 Bug 单。
