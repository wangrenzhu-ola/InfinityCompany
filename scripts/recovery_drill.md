# 恢复能力演练手册 (Recovery Drill)

本演练手册用于验证在全新或升级后的 OpenClaw 基座上，能否通过 InfinityCompany 仓库完整恢复虚拟公司的运行能力。建议每月执行一次深度演练。

## 演练准备
1. 准备一个干净的测试服务器或虚拟机。
2. 安装基础的 OpenClaw 环境（参考最新版文档）。
3. 确保有权限拉取 `InfinityCompany` 仓库。

## 演练 1：全量重建演练 (Cold Start)

### 步骤
1. **克隆仓库**: 
   ```bash
   git clone git@github.com:wangrenzhu-ola/InfinityCompany.git
   cd InfinityCompany
   ```
2. **环境初始化**: 
   复制 `.env.example` 到 `.env` 并填入测试用的 Notion API Key 和模型 Key。
   ```bash
   cp .env.example .env
   # 编辑 .env
   ```
3. **执行附着**:
   ```bash
   ./scripts/attach-openclaw.sh .env
   ```
4. **部署覆盖**:
   ```bash
   ./scripts/deploy-overlay.sh .env
   ```

### 预期结果
- 脚本执行无报错退出。
- 目标目录 `~/.openclaw/agents/` 下成功生成了 10 个角色的配置文件。
- `openclaw agent list` 能够正确识别所有角色。

## 演练 2：知识库恢复演练

### 步骤
1. **执行 OpenViking 恢复**:
   ```bash
   openviking restore --from-backup latest
   ```
2. **触发全量同步**:
   ```bash
   openviking sync --full
   ```

### 预期结果
- 向量数据库被正确重建。
- `openviking memory search "测试"` 能够返回历史沉淀的设计规范或上下文。

## 演练 3：灾难回滚演练

### 步骤
1. 故意修改 `~/.openclaw/agents/caocan/IDENTITY.md` 制造配置破坏。
2. 执行回滚：
   ```bash
   ./scripts/rollback-overlay.sh
   ```
3. 重新执行验证脚本：
   ```bash
   ./scripts/validate-overlay.sh
   ```

### 预期结果
- 破坏的配置被还原，系统恢复到上一次成功 deploy 时的稳定快照。
