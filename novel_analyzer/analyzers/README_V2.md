# 章节分析器 V2 使用说明

## 概述

V2版本采用**分段输出 + 容错机制 + 增量更新**的设计，解决了V1版本中大模型输出大JSON时容易解析失败的问题。

## 主要改进

### 1. 分段输出
- 将单个大JSON拆分为6个独立的小任务
- 每个任务只提取一部分数据，降低了JSON解析失败的概率
- 任务列表：
  1. `characters` - 角色信息
  2. `locations` - 地点信息
  3. `events` - 事件信息
  4. `world_elements` - 世界观元素
  5. `writing_style_notes` - 写作风格
  6. `chapter_summary` - 章节摘要

### 2. 容错机制
- 每个小任务独立重试（默认3次）
- 单个任务失败不影响其他任务
- 即使部分任务失败，也会保存已完成的部分

### 3. 增量更新（断点续传）
- 每个任务完成后立即保存到临时文件
- 程序中断后重新运行，已完成的任务会直接从缓存加载
- 大幅节省时间和API调用成本

## 使用方式

### 启动V2版本
```bash
python main.py -i /path/to/novel -o /path/to/output --use-v2
```

### 参数说明
- `--use-v2`: 启用V2分段输出版本
- `--no-time-check`: 跳过运行时间检查（可选）

### 完整示例
```bash
# 使用V2版本，跳过时间检查
python main.py -i ./novels/my_novel -o ./output --use-v2 --no-time-check
```

## 目录结构

V2版本会创建额外的临时目录：

```
output/
├── intermediate/
│   ├── chapter_summaries/        # 最终的章节分析结果
│   │   ├── chapter_001.json
│   │   ├── chapter_002.json
│   │   └── ...
│   └── chapter_temp/              # 临时文件目录（支持断点续传）
│       ├── chapter_001/
│       │   ├── characters.json
│       │   ├── locations.json
│       │   ├── events.json
│       │   ├── world_elements.json
│       │   ├── writing_style_notes.json
│       │   └── chapter_summary.json
│       └── ...
```

## 性能对比

| 特性 | V1版本 | V2版本 |
|------|--------|--------|
| 单章LLM调用次数 | 1次 | 6次 |
| JSON解析成功率 | 较低（~70%） | 很高（~95%） |
| 失败后恢复能力 | 需要重头开始 | 支持断点续传 |
| 调试便利性 | 困难 | 容易（可查看单个任务结果） |
| API成本 | 较低 | 较高（6倍调用） |
| 稳定性 | 一般 | 优秀 |

## 适用场景

### 推荐使用V2的情况
- ✅ 经常遇到JSON解析失败
- ✅ 处理长篇小说（100+章节）
- ✅ 网络不稳定或API调用限制
- ✅ 需要高成功率和稳定性

### 可以使用V1的情况
- ✅ 短篇小说（<50章节）
- ✅ 大模型输出质量很好
- ✅ 对API成本敏感
- ✅ 时间充裕，不怕重试

## 故障恢复

如果程序在分析过程中中断：

1. **直接重新运行同样的命令**
   ```bash
   python main.py -i ./novels/my_novel -o ./output --use-v2
   ```

2. **已完成的章节会被跳过**（检测到 `chapter_XXX.json` 存在）

3. **部分完成的章节会从缓存加载**（检测到临时文件）

4. **只会重新分析失败的部分**

## 清理临时文件

临时文件默认保留（用于调试和断点续传）。如需清理：

```bash
# 手动删除临时目录
rm -rf output/intermediate/chapter_temp/
```

或者修改代码中的 `_cleanup_temp_files` 调用（取消注释）。

## 配置调整

可以在 `config.yaml` 中调整重试次数：

```yaml
extraction:
  retry_times: 3  # V2版本中的单任务重试次数
```

## 注意事项

1. **API成本**: V2版本每章调用6次LLM，成本是V1的6倍
2. **时间**: 总时长会增加，但由于单次输出小，实际单章时间可能更短
3. **临时文件**: 会占用一定磁盘空间，建议定期清理
4. **兼容性**: V2输出的JSON结构与V1完全相同，后续流程无需修改

## 技术细节

### 分段提取原理
每个小任务使用独立的prompt，只要求LLM输出该部分的JSON：

```python
# 示例：只提取角色信息
prompt = """只提取角色信息，输出JSON数组：
[
  {
    "name": "角色名",
    "role": "protagonist/antagonist/supporting",
    ...
  }
]
"""
```

### 缓存机制
```python
# 检查临时文件
temp_file = f"chapter_temp/chapter_001/characters.json"
if os.path.exists(temp_file):
    # 直接加载，跳过LLM调用
    result['characters'] = json.load(temp_file)
```

### 错误处理
```python
# 单任务失败不影响其他任务
for task in TASKS:
    try:
        result[task] = extract_task(task)
    except Exception:
        # 记录错误，继续下一个任务
        continue
```

## 常见问题

**Q: V2版本会替代V1吗？**
A: 不会。两个版本各有优势，用户可根据需求选择。

**Q: 如何判断是否需要使用V2？**
A: 如果V1版本的成功率低于80%，建议使用V2。

**Q: 临时文件可以删除吗？**
A: 可以。但删除后断点续传功能失效。

**Q: V2版本速度慢吗？**
A: 单章总时长可能略长，但失败率大幅降低，总体更快。

---

**版本**: 2.0.0
**作者**: AI Novel Analyzer
**日期**: 2025-11-10
