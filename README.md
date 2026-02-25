# Agent-Learn - AI代理学习项目

这是一个系统化的AI代理学习项目，专注于Claude的函数调用、代理循环、上下文管理等核心概念。

## 项目结构

```
agent-learn/
├── config/              配置文件
├── context_manager/     上下文管理模块
├── function_call/       函数调用核心模块
├── llm/                 LLM 客户端封装
├── task_decomposer/     任务分解模块
├── task_planner/        任务规划模块
├── subagent/            子代理模式演示
├── tools/               工具集合
├── utils/               工具函数
├── logs/                统一日志目录（所有模块共享）
└── requirements.txt     依赖包列表
```

## 日志管理

所有模块的日志文件统一存储在项目根目录的 `logs/` 文件夹中，便于集中管理和查看。

### 日志文件命名规范
- 格式：`{模块名}_{时间戳}.log`
- 示例：`app_20260219_193155.log`, `task_decomposer_20260219_193235.log`

### 查看日志
```bash
# 查看最新日志
tail -f logs/app_*.log

# 查看特定模块日志
ls logs/task_decomposer_*.log
```

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env_template .env
# 编辑 .env 文件，填入你的API密钥
```

3. 运行示例：
```bash
# 函数调用演示
cd function_call && python main.py

# 任务分解演示  
cd task_decomposer && python demo.py

# 任务规划演示
cd task_planner && python demo.py

# 子代理模式演示
cd subagent && python main.py
```

## 核心概念

- **函数调用**：模型与外部工具交互的基础
- **代理循环**：持续执行任务的核心机制
- **上下文管理**：处理长期运行任务的关键
- **工具生态**：操作现实世界的能力基础

## Agent 由浅入深学习计划

推荐把本仓库作为「动手实验场」，结合 [learn-claude-code](../learn-claude-code) 的完整教学内容，一起理解 Agent 的核心概念。可以按下面顺序学习：

### 第 1 步：理解模型如何调用工具

- 目标：知道「模型不仅会说话，还能通过工具真正做事」
- 建议：
  - 阅读并运行 [function_call/main.py](./function_call/main.py)
  - 对照 learn-claude-code 中的 v1 相关文档，理解 Agent 循环和工具分发

### 第 2 步：掌握上下文管理的基本模式

- 目标：理解多轮对话和长任务下，如何管理上下文大小和结构
- 建议：
  - 阅读并运行 [context_manager/main.py](./context_manager/main.py)
  - 体会上下文监控、统计与压缩的基本思路，再对照 learn-claude-code 的 v5 上下文压缩机制

### 第 3 步：让任务分解和规划显式化

- 目标：从「模型心里有计划」走向「计划写在任务列表里」
- 建议：
  - 阅读并运行 [task_decomposer/demo.py](./task_decomposer/demo.py)，关注如何用 LLM 把自然语言目标拆成步骤
  - 阅读并运行 [task_planner/demo.py](./task_planner/demo.py)，关注：
    - LLM 直接输出 JSON 任务计划
    - 如何映射到本地 Task 对象和 TaskPlanner
  - 对照 learn-claude-code 中 v2、v6 的 Todo/Tasks 设计，加深对显式规划和任务系统的理解

### 第 4 步：体验子代理模式（Subagent）

- 目标：理解「主代理拆分目标，子代理各司其职」的协作模式
- 建议：
  - 阅读并运行 [subagent/main.py](./subagent/main.py)
    - 主代理只负责接收用户目标、决定调用哪些子代理
    - PlannerSubagent 负责拆分任务
    - ImplementSubagent 负责细化具体执行方案
  - 对照 learn-claude-code 中 v3 子代理机制，思考：
    - 子代理是否可以拥有独立的工具集与上下文
    - 如何把这里的简单示例演进成真正的子 Agent 系统

### 第 5 步：回到完整框架中定位这些能力

- 在理解本仓库四个 demo 之后，再回到 learn-claude-code：
  - 把这里的函数调用、上下文管理、任务分解/规划、子代理，对应到 v1、v3、v5、v6 等版本
  - 从更「工程化」的实现里，看到这些概念是如何组合成一个可用的 AI 编程代理的

这样，你可以一边用 agent-learn 做小而清晰的实验，一边在 learn-claude-code 中观察「同一概念在完整系统中的样子」，由浅入深地建立自己的 Agent 心智模型。

## 开发规范

- 遵循统一的日志配置
- 使用项目根目录相对路径
- 保持模块间的低耦合
- 文档与代码同步更新
