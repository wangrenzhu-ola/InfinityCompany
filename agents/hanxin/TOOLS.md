# 韩信 的工具集

## 必备技能 (Skills)

### 代码开发与编辑
- **VS Code / Cursor / Windsurf**: 主力代码编辑器，用于前后端代码开发、AI辅助编程
- **Git**: 版本控制，代码提交、分支管理、代码合并
- **GitHub**: 代码托管、Pull Request、Code Review、Actions CI/CD

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
