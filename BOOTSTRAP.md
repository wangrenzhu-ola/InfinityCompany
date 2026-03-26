# Clawpanel 本地部署基线

## 当前基线

- 代码位置：`/Users/wangrenzhu/work/MetaClaw/clawpanel`
- 启动方式：`docker compose up -d --build`
- 容器名：`clawpanel`
- 网络模式：`bridge + ports`
- OpenClaw 配置挂载：`~/.openclaw:/root/.openclaw`
- 数据目录挂载：`./data:/app/data`
- OpenClaw Gateway 地址：`http://127.0.0.1:18789`
- ClawPanel 地址：`http://127.0.0.1:1420/`
- 容器内 OpenClaw 地址：`http://host.docker.internal:18789`
- 时区：`Asia/Shanghai`
- Web 健康检查地址：`http://localhost:1420/`

## 运行前提

- 本机已安装 Docker 与 Docker Compose
- 本机已有可用的 OpenClaw 运行环境
- `~/.openclaw` 目录可被容器挂载
- `openclaw` CLI 已可用

## 建议检查项

- OpenClaw Gateway 已在 `127.0.0.1:18789` 可访问
- `docker compose ps` 中 `clawpanel` 状态正常
- `curl http://localhost:1420/` 返回 200

## 推荐入口

```bash
./Init-InfinityCompany.command
./Open-InfinityCompany.command
```

- 初始化入口会自动生成 `configs/openclaw-target.local.env`
- 初始化入口会执行 `deploy-overlay.sh`，然后拉起 Gateway 与 ClawPanel
- 日常入口会检查 Gateway 健康状态、必要时重启服务，并弹出 token 与访问链接
