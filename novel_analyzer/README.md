# 爆款小说分析工具

基于LangChain和Ollama的智能小说分析系统，采用分层概括策略处理长篇小说。

## 功能特性

- ✅ 逐章提取角色、地点、事件、世界观要素
- ✅ 分段汇总（每20章）
- ✅ 整体分析和模板生成
- ✅ 生成5个标准化创作模板

## 快速开始

### 1. 安装依赖

```bash
cd novel_analyzer
pip install -r requirements.txt
# 或使用 pipenv
pipenv install
```

### 2. 配置LLM

复制环境变量模板并编辑：

```bash
cp ../.env.example ../.env
# 编辑 .env 文件，填入你的LLM配置
```

**支持两种LLM方式：**

#### 方式A: OpenAI兼容接口（推荐）

编辑 `.env` 文件：
```bash
LLM_PROVIDER=openai
OPENAI_API_BASE=http://your-api-endpoint/
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=your_model_name
```

#### 方式B: Ollama本地模型

1. 安装 [Ollama](https://ollama.ai)
2. 下载模型：`ollama pull qwen2.5:7b-instruct`
3. 启动服务：`ollama serve`
4. 编辑 `.env` 文件：
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
```

详细配置说明请查看 [CONFIG.md](CONFIG.md)

## 使用方法

### 基本用法

```bash
python main.py --input /path/to/novel/folder --output /path/to/output
```

### 参数说明

- `--input, -i`: 小说文件夹路径（必需，包含多个txt章节文件）
- `--output, -o`: 输出目录路径（必需）
- `--config, -c`: 配置文件路径（可选，默认使用config/config.yaml）

### 示例

```bash
# 分析《斗破苍穹》
python main.py \
  --input ./data/input_novels/斗破苍穹/ \
  --output ./data/output_templates/斗破苍穹_template/
```

## 输入格式

小说文件夹应包含按章节分割的txt文件：

```
斗破苍穹/
├── 第001章.txt
├── 第002章.txt
├── 第003章.txt
└── ...
```

文件名应包含章节序号，以便正确排序。

## 输出结构

```
output_directory/
├── intermediate/
│   ├── chapter_summaries/
│   │   ├── chapter_001.json  # 第1章分析结果
│   │   ├── chapter_002.json
│   │   └── ...
│   ├── segment_summaries/
│   │   ├── segment_001-020.json  # 第1-20章汇总
│   │   ├── segment_021-040.json
│   │   └── ...
│   └── global_analysis.json  # 整体分析结果
├── world_bible.json          # 世界观圣经
├── plot_framework.json       # 情节框架
├── writing_guide.json        # 写作指南
├── character_templates.json  # 角色模板
└── quality_criteria.json     # 质量标准
```

## 配置说明

编辑 `config/config.yaml` 调整参数：

```yaml
llm:
  model: "qwen2.5:7b-instruct"  # 使用的模型
  temperature: 0.3               # 生成温度

processing:
  segment_size: 20               # 每个分段的章节数

preprocessing:
  min_chapter_length: 500        # 最小章节字数
  max_chapter_length: 20000      # 最大章节字数
```

## 分析流程

```
1️⃣ 文件预处理
   ├─ 加载所有txt文件
   ├─ 文本清洗
   └─ 统计信息

2️⃣ 单章分析（逐章）
   ├─ 提取角色信息
   ├─ 提取地点信息
   ├─ 提取事件信息
   ├─ 提取世界观要素
   └─ 分析写作风格

3️⃣ 分段汇总（每20章）
   ├─ 合并角色信息
   ├─ 概括剧情发展
   ├─ 整合世界观
   └─ 提取写作模式

4️⃣ 整体分析
   ├─ 综合所有分段
   ├─ 提取核心要素
   └─ 生成整体视图

5️⃣ 模板生成
   ├─ world_bible.json - 世界观设定
   ├─ plot_framework.json - 情节结构
   ├─ writing_guide.json - 写作风格
   ├─ character_templates.json - 角色设定
   └─ quality_criteria.json - 质量标准
```

## 处理时间估算

- 单章分析: 约5-10秒/章
- 分段汇总: 约10-20秒/分段
- 整体分析: 约20-30秒
- 模板生成: 约5秒
- **100章小说完整流程**: 约20-35分钟

## 注意事项

1. **确保Ollama服务运行**：执行前确认 `ollama serve` 已启动
2. **章节文件格式**：txt文件需UTF-8编码
3. **硬盘空间**：中间文件会占用一定空间
4. **网络连接**：首次使用会下载模型文件

## 故障排除

### Ollama连接失败

```
错误: Could not connect to Ollama
解决: 检查Ollama服务是否启动（ollama serve）
```

### JSON解析失败

```
错误: JSON解析失败
解决: 系统会自动重试3次，如仍失败会跳过该章节
```

### 内存不足

```
解决: 减小 config.yaml 中的 segment_size 参数
```

## 最终模板说明

### 1. world_bible.json - 世界观圣经
包含世界类型、地理、力量体系、社会结构等完整世界观设定

### 2. plot_framework.json - 情节框架
包含故事结构、主支线情节、冲突类型、节奏模式等

### 3. writing_guide.json - 写作指南
包含语气、语言风格、叙事技巧、情感表达等写作指导

### 4. character_templates.json - 角色模板
包含主要角色的性格、背景、能力、成长弧线等

### 5. quality_criteria.json - 质量标准
包含主题一致性、情节质量、角色质量、写作质量等评估标准

## 开发状态

- [x] Phase 1: 基础框架
- [x] Phase 2: 单章分析器
- [x] Phase 3: 分段汇总器
- [x] Phase 4: 整体分析器
- [x] Phase 5: 模板生成器
- [ ] Phase 6: 完整测试和优化

## 许可证

MIT License
