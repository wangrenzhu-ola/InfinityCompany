# Scheduler Skill

定时任务调度器，用于执行 InfinityCompany 的每日定时任务。

## 功能

- 基于 cron 的定时任务调度
- 支持每日时间表任务
- 任务执行日志记录
- 任务失败告警

## 使用方法

```bash
# 启动定时任务调度器
python3 scheduler.py start

# 查看任务列表
python3 scheduler.py list

# 手动触发任务
python3 scheduler.py run <task_name>

# 查看执行日志
python3 scheduler.py logs
```
