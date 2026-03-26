# 夏侯婴 初始化指南

## 环境依赖
- 依赖 InfinityCompany 基础环境配置
- 确保已正确配置 MiniMax-M2.7-highspeed 模型的 API Key
- 确保已配置 Notion 外部需求看板的读取权限

## 初始化动作
1. 验证 `IDENTITY.md` 和 `SOUL.md` 是否已正确加载
2. 检查必要的工具权限是否已开启（git、notion、意图识别、健康管理）
3. 读取当前迭代的看板状态，明确今日任务
4. 验证 Notion 外部需求看板的连接状态
5. 检查 `dispatch.log` 文件是否存在，不存在则创建

## 首次启动检查清单
- [ ] IDENTITY.md 中的模型声明正确（MiniMax-M2.7-highspeed）
- [ ] Notion 外部需求看板读取权限已配置
- [ ] 定时任务（08:30、09:15、09:25、11:25、16:55、17:25）已设置
- [ ] `agents/xiahouying/dispatch.log` 文件已创建
- [ ] 与郦食其（外部助理）的协作链路已确认
