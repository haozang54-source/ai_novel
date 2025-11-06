# 快速开始指南

## 第一步：安装依赖

```bash
cd novel_analyzer
bash setup.sh
```

或者手动安装：

```bash
python3 -m pip install langchain langchain-community python-dotenv pyyaml pydantic tqdm
```

## 第二步：确保Ollama运行

### 检查Ollama是否安装

```bash
ollama --version
```

### 检查模型是否存在

```bash
ollama list
```

应该看到 `qwen2.5:7b-instruct` 在列表中。

### 启动Ollama服务（如果未运行）

```bash
ollama serve
```

## 第三步：测试运行

使用项目自带的测试小说：

```bash
python3 main.py \
  --input ./data/input_novels/test_novel/ \
  --output ./data/output_templates/test_output/
```

## 第四步：查看结果

成功后，查看输出目录：

```bash
ls -la ./data/output_templates/test_output/intermediate/
```

应该看到：
- `chapter_summaries/` - 单章分析结果
- `segment_summaries/` - 分段汇总结果

## 使用自己的小说

1. 将小说章节文件（txt格式）放到一个文件夹中
2. 文件名应该能体现章节顺序，如：
   - `第001章.txt`
   - `第002章.txt`
   - 或 `chapter_001.txt` 等

3. 运行分析：

```bash
python3 main.py \
  --input /path/to/your/novel/ \
  --output /path/to/output/
```

## 常见问题

### Q: 提示 "Could not connect to Ollama"

A: 确保Ollama服务正在运行：
```bash
# 新开一个终端窗口运行
ollama serve
```

### Q: 分析速度太慢

A: 这是正常的，qwen2.5:7b 模型需要一定处理时间
- 单章分析约需 5-15秒
- 可以先用2-3章测试

### Q: JSON解析失败

A: 系统会自动重试3次，如果仍失败会跳过该章节
- 检查模型是否正常
- 可以减少章节长度限制

## 下一步

- 查看生成的JSON文件了解提取的信息
- 等待第三层整体分析功能完成
- 使用生成的模板进行小说创作

## 项目结构

```
novel_analyzer/
├── main.py                  # 主程序
├── config/config.yaml       # 配置文件
├── analyzers/              # 分析器模块
├── utils/                  # 工具模块
├── data/
│   ├── input_novels/       # 输入小说
│   └── output_templates/   # 输出结果
└── logs/                   # 日志文件
```
