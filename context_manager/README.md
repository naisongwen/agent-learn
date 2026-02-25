# Claude Context Manager

## 项目概述

Claude Context Manager 是一个遵循 agent-learn 项目规范的上下文管理演示系统，展示了 Claude AI 代理在处理复杂对话时的核心上下文管理能力。

## 目录结构

```
context_manager/
├── main.py              # 主入口文件
├── README.md           # 说明文档
└── __pycache__/        # Python 缓存目录
```

## 核心功能

### 1. 上下文管理
- **智能令牌监控**: 实时跟踪上下文令牌使用情况
- **自动压缩机制**: 基于阈值的智能上下文压缩
- **消息生命周期管理**: 完整的消息存储和检索系统

### 2. 标准工具接口
- **ContextManagerTool**: 符合 agent-learn 规范的标准工具
- **多种操作模式**: 监控、压缩、统计、清空、获取最近消息
- **OpenAI 兼容格式**: 支持标准的工具调用格式

### 3. 核心概念演示
- **函数调用模拟**: 展示 Claude 与外部工具的交互
- **代理循环演示**: 完整的思考-行动-观察循环
- **上下文管理验证**: 实时监控和智能压缩效果

## 使用方法

### 1. 直接运行
```bash
cd agent-learn/context_manager
python main.py
```

### 2. 模块方式导入
```python
import context_manager.main
# 或者
from context_manager import main
```

### 3. 使用标准工具接口
```python
from tools import get_tool_by_name

# 获取上下文管理工具
context_tool = get_tool_by_name("manage_context")

# 执行各种操作
monitor_result = context_tool.execute("monitor")
stats_result = context_tool.execute("stats")
compress_result = context_tool.execute("compress")
```

## 核心组件

### ContextManager (核心类)
位于: `tools/context_manager.py`

主要功能:
- 消息管理和存储
- 令牌计数和监控
- 智能上下文压缩
- 统计信息生成

### ContextManagerTool (工具类)
位于: `tools/context_manager.py`

标准工具接口:
- `to_openai_format()`: 转换为 OpenAI 工具格式
- `execute(action, **kwargs)`: 执行具体操作
- 支持的操作: monitor, compress, stats, clear, recent

## 演示场景

### 场景1: 函数调用模拟
```
演示 Claude 如何通过函数调用与外部工具交互
- 计算工具调用
- 天气查询工具调用
- 文件操作工具调用
```

### 场景2: 代理循环模拟
```
展示完整的代理执行循环
- 用户请求处理
- 工具调用执行
- 结果反馈和继续执行
```

### 场景3: 上下文管理功能
```
验证上下文管理的各项功能
- 实时监控和统计
- 智能压缩效果
- 消息检索和管理
```

## 技术规范

### 遵循的标准
- **agent-learn 项目规范**: 完全兼容现有工具体系
- **分层架构**: 工具层与演示层分离
- **接口一致性**: 保持向后兼容性

### 默认配置
- 最大上下文长度: 4000 tokens
- 压缩阈值: 80% (3200 tokens)
- 保留策略: 用户消息 + 最近5条系统消息
- 令牌估算: 字符数 × 0.3

## 最佳实践

### 1. 上下文监控
- 定期检查令牌使用情况
- 在达到70-80%使用率时考虑压缩
- 根据任务复杂度调整监控频率

### 2. 压缩策略
- 长时间运行任务定期压缩
- 大量工具调用后及时压缩
- 保持关键信息的完整性

### 3. 性能优化
- 合理设置压缩参数
- 避免频繁的压缩操作
- 根据硬件资源调整配置

## 扩展方向

### 1. 高级功能
- 基于语义的智能压缩
- 上下文摘要自动生成
- 跨会话上下文持久化

### 2. 集成优化
- 与具体 LLM 的深度集成
- 自适应压缩策略
- 实时性能监控

### 3. 企业级特性
- 多用户上下文隔离
- 上下文使用配额管理
- 详细的审计日志

## 故障排除

### 常见问题
1. **导入错误**: 确保在 agent-learn 项目根目录下运行
2. **工具找不到**: 检查 tools/__init__.py 中的工具注册
3. **压缩效果不佳**: 调整压缩阈值和保留策略

### 调试建议
- 启用详细日志记录
- 使用统计功能分析使用模式
- 逐步测试各项功能

## 相关资源

- [agent-learn 项目](../README.md)
- [工具系统文档](../tools/README.md)
- [函数调用演示](../function_call/README.md)

这个上下文管理系统为理解和实现 Claude AI 代理的上下文管理提供了完整的参考实现和最佳实践指导。