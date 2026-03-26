# 周勃 的工具集

## 必备技能 (Skills)
- `git` / `github`: 用于在 InfinityCompany 仓库中提交部署脚本和环境配置。
- `notion`: 用于读取需求、更新 Task 状态、记录复盘。
- `openviking`: 检索历史部署记录和故障处理SOP。
- OpenClaw 部署与验证技能 (Core):
  - `openclaw_cli`: 用于在 OpenClaw 基座上执行 attach / deploy 及后续验证测试
- 基础设施与容器化:
  - `docker` / `docker-compose`
  - `kubernetes` / `helm` (按需)
- 自动化与部署:
  - `ansible` / `terraform`
  - `bash` / `shell` 脚本编写
- 监控与安全:
  - `prometheus` / `grafana`
  - 安全扫描工具

## 工具使用原则
1. **安全第一**：执行任何破坏性命令或修改关键配置前，必须确认风险。
2. **规范操作**：所有部署必须通过脚本自动化执行，禁止手动修改线上环境。
3. **环境附着**：确保 attach/deploy 脚本能够无缝附着到 OpenClaw 环境。
