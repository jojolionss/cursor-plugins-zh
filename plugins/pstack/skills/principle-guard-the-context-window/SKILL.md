---
name: principle-guard-the-context-window
description: "适用于上下文越来越满时:大体积输出、长文件、重复读取、fan-out 规划。把大块内容路由给子代理;主线程只保留摘要,不放原始载荷。"
disable-model-invocation: true
---

# Guard the Context Window

**Why:** Context overflow degrades reasoning quality, creates compression artifacts, and halts progress.

**Pattern:**
- **Size phases and cap scope.** Limit files per phase, set turn budgets, account for mechanism costs.
