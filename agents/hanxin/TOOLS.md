# 韩信 的工具集

## 必备技能 (Skills)

### 代码开发与编辑
- **Kimi Code CLI**: 编码执行器，用于生成/修改代码文件、创建脚本和项目（主要工具）
- **VS Code / Cursor / Windsurf**: 辅助代码编辑器，用于代码审查和轻量编辑
- **Git**: 版本控制，代码提交、分支管理、代码合并
- **GitHub**: 代码托管、Pull Request、Code Review、Actions CI/CD

### Kimi Code CLI 工作流程

#### 架构分工
- **会话模型**（我）：需求澄清、任务拆解、验收标准、结果核查、复盘总结
- **Kimi CLI**：按指令在指定目录里创建/修改文件、生成脚本/项目、给出执行步骤

#### 两种工作模式

**1. 快速模式 (Quick Mode)**
适用于明确的单次任务，执行完即返回。

```bash
# 必需参数：pty:true（分配伪终端，确保输出稳定）
# 推荐 workdir 使用独立项目目录
# timeout 建议：简单任务 300s，复杂项目 600s

exec(command="kimi --print -p '任务描述'", pty=true, workdir="~/projects/my-project", timeout=300)
```

示例：
```bash
# 创建项目
exec(command="kimi --print -p '创建一个 React + TypeScript 的待办事项应用'", pty=true, workdir="~/projects", timeout=600)

# 重构代码
exec(command="kimi --print -p '重构 src/utils.py 使用现代 Python 最佳实践'", pty=true, workdir="~/my-project", timeout=300)
```

**2. 交互模式 (Interactive Mode)**
适用于复杂任务需要多轮交互，或 Kimi 可能会提问确认。

```bash
exec(command="kimi", pty=true, workdir="~/project", background=true)
# 后续通过 process 工具控制
```

#### 注意事项
- 优先使用 Quick Mode（`kimi --print`），避免进入交互模式导致输出不一致
- 不要用 `kimi '...'` 作为 one-shot 标准写法
- Kimi CLI 安装路径：`/Users/wangrenzhu/.local/bin/kimi`

### 编程语言
- **Python**: 后端开发、AI/ML脚本、自动化工具
- **JavaScript / TypeScript**: 前端交互、Node.js后端服务
- **Node.js**: JavaScript运行时，用于构建服务端应用

### 前端框架与工具
- **React**: 构建用户界面的核心库
- **Vue.js**: 渐进式前端框架（按需使用）
- **Tailwind CSS / Styled Components**: UI样式开发
- **Webpack / Vite**: 前端构建工具

### 后端框架与API
- **FastAPI**: 高性能Python Web框架，用于API开发
- **Flask**: 轻量级Python Web框架
- **Express.js**: Node.js Web应用框架
- **RESTful API / GraphQL**: API设计与实现规范

### AI与自动化
- **OpenAI API / Claude API**: LLM调用集成
- **LangChain / LlamaIndex**: AI工作流编排框架
- **Hugging Face**: AI模型库与工具

### 数据存储
- **PostgreSQL**: 关系型数据库，主数据存储
- **MongoDB**: 文档型数据库，非结构化数据存储
- **Redis**: 内存缓存、消息队列、会话存储

### 容器与部署
- **Docker**: 容器化应用打包与运行
- **Docker Compose**: 多容器本地编排

### 协作与文档
- **Notion**: 需求读取、任务状态更新、技术文档
- **Slack**: 团队即时沟通
- **GitHub Issues / Projects**: 问题追踪与项目管理

## 工具使用原则

1. **安全第一**: 
   - 执行任何破坏性命令或修改关键配置前，必须确认风险
   - 数据库操作前务必备份，生产环境变更需双重确认

2. **规范操作**: 
   - 代码提交遵循 Conventional Commits 规范
   - 分支管理采用 Git Flow 或 Trunk Based 策略
   - 所有代码需通过 PR Review 后方可合并

3. **留痕优先**: 
   - 所有技术决策记录在 Notion 或 GitHub Issues
   - 复杂功能需编写技术设计文档

4. **质量保障**: 
   - 核心代码需配套单元测试
   - 使用 TypeScript 提升代码健壮性
   - 关键路径添加日志与监控
