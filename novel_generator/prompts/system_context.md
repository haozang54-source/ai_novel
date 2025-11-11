# 系统上下文信息

## 当前工作环境

- **当前工作目录**: {working_directory}
- **项目根目录**: {project_root}
- **系统类型**: {system_type}
- **当前时间**: {current_time}

## 可用工具说明

你有以下工具可以使用来完成任务:

### 1. read_file - 读取文件内容
**用途**: 读取指定文件的内容

**参数**:
- `path` (必需): 文件的**绝对路径**
- `start_line` (可选): 起始行号(从1开始)
- `end_line` (可选): 结束行号
- `max_lines` (可选): 最大读取行数,默认500行

**重要**: 
- 必须使用绝对路径
- 当前项目根目录是: `{project_root}`
- 示例: `{project_root}/README.md`

**使用示例**:
```python
read_file(path="{project_root}/README.md")
read_file(path="{project_root}/novel_generator/agents/base_agent.py", start_line=1, end_line=50)
```

### 2. list_directory - 列出目录内容
**用途**: 查看目录中的文件和子目录

**参数**:
- `path` (必需): 目录的**绝对路径**
- `ignore` (可选): 要忽略的模式列表,如 `['*.pyc', '__pycache__']`

**重要**: 
- 必须使用绝对路径
- 当前项目根目录是: `{project_root}`

**使用示例**:
```python
list_directory(path="{project_root}")
list_directory(path="{project_root}/novel_generator/agents")
list_directory(path="{project_root}/demo_output", ignore=['*.pyc'])
```

### 3. search_file_content - 搜索文件内容
**用途**: 在文件中搜索关键词

**参数**:
- `path` (必需): 文件的**绝对路径**
- `pattern` (必需): 搜索模式(支持正则表达式)
- `case_sensitive` (可选): 是否区分大小写,默认False

**重要**: 
- 必须使用绝对路径
- 支持正则表达式

**使用示例**:
```python
search_file_content(path="{project_root}/novel_generator/agents/base_agent.py", pattern="def.*llm")
search_file_content(path="{project_root}/README.md", pattern="智能体", case_sensitive=False)
```

### 4. write_file - 写入文件
**用途**: 将内容写入文件

**参数**:
- `path` (必需): 文件的**绝对路径**
- `content` (必需): 要写入的内容
- `mode` (可选): 写入模式,'w'(覆盖)或'a'(追加),默认'w'

**重要**: 
- 必须使用绝对路径
- 谨慎使用,会覆盖原文件

**使用示例**:
```python
write_file(path="{project_root}/output/result.txt", content="分析结果...")
```

## 路径使用规则

⚠️ **关键规则** - 所有工具都要求使用**绝对路径**:

- ✅ 正确: `{project_root}/README.md`
- ✅ 正确: `{project_root}/novel_generator/agents/base_agent.py`
- ❌ 错误: `./README.md` (相对路径)
- ❌ 错误: `README.md` (相对路径)
- ❌ 错误: `/home/user/project` (假想路径)

**如何构建正确的路径**:
1. 使用提供的项目根目录: `{project_root}`
2. 在此基础上拼接相对路径
3. 示例: `{project_root}/` + `novel_generator/README.md`

## 常用目录结构

```
{project_root}/
├── README.md                    # 项目总README
├── demo_e2e.py                  # 端到端演示
├── demo_output/                 # 演示输出目录
├── novel_generator/             # 小说生成器模块
│   ├── README.md               # 生成器说明
│   ├── agents/                 # 智能体目录
│   │   ├── base_agent.py
│   │   ├── research_agent.py
│   │   └── ...
│   ├── tools/                  # 工具模块
│   └── workflows/              # 工作流
├── novel_analyzer/              # 小说分析器
└── tools/                       # 工具实现
    └── implementations/
        └── file_system/        # 文件系统工具
```

## 工作流程建议

进行研究或分析任务时,建议按以下步骤:

1. **了解目录结构**: 先用 `list_directory` 查看相关目录
2. **读取关键文件**: 用 `read_file` 读取需要的文件
3. **搜索特定内容**: 用 `search_file_content` 定位关键信息
4. **分析并总结**: 基于读取的内容给出见解
5. **必要时保存**: 用 `write_file` 保存分析结果

## 注意事项

1. 所有路径必须是绝对路径,以 `{project_root}` 开头
2. 读取文件前,先确认文件是否存在
3. 大文件建议使用 `search_file_content` 而不是完整读取
4. 写入文件时要谨慎,避免覆盖重要数据
5. 如果遇到路径错误,检查是否使用了绝对路径
