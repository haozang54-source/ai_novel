# 配置说明

## 环境变量配置（推荐）

### 1. 复制环境变量模板

```bash
cp ../.env.example ../.env
```

### 2. 编辑 `.env` 文件

```bash
# OpenAI兼容接口配置
OPENAI_API_BASE=http://your-api-endpoint/
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_name

# LLM提供商选择
LLM_PROVIDER=openai  # 或 ollama

# LLM参数
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=3000
```

### 3. 支持的配置项

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `LLM_PROVIDER` | LLM提供商 (openai/ollama) | ollama |
| `OPENAI_API_BASE` | OpenAI API地址 | - |
| `OPENAI_API_KEY` | OpenAI API密钥 | dummy |
| `OPENAI_MODEL` | OpenAI模型名称 | gpt-3.5-turbo |
| `OLLAMA_BASE_URL` | Ollama服务地址 | http://localhost:11434 |
| `OLLAMA_MODEL` | Ollama模型名称 | qwen2.5:7b-instruct |
| `LLM_TEMPERATURE` | 温度参数 | 0.3 |
| `LLM_MAX_TOKENS` | 最大Token数 | 3000 |

## 配置文件方式（可选）

如果不使用环境变量，也可以直接修改 `config/config.yaml`：

```yaml
llm:
  provider: "openai"
  model: "your_model_name"
  base_url: "http://your-api-endpoint/"
  api_key: "your_api_key"
  temperature: 0.3
  max_tokens: 3000
```

⚠️ **注意**：配置文件中的敏感信息会被提交到git，不推荐此方式。

## 优先级

环境变量 > config.yaml

即：如果同时配置了环境变量和config.yaml，会优先使用环境变量中的值。

## 安全建议

1. ✅ **推荐**：使用 `.env` 文件存储敏感信息（已自动忽略）
2. ✅ **推荐**：使用环境变量配置
3. ❌ **不推荐**：在 `config.yaml` 中直接写入API密钥
4. ❌ **禁止**：提交包含真实API密钥的文件到git

## 示例

### 使用OpenAI兼容接口

```bash
# .env 文件
LLM_PROVIDER=openai
OPENAI_API_BASE=http://your-endpoint/
OPENAI_API_KEY=your_key
OPENAI_MODEL=your_model
```

### 使用Ollama本地模型

```bash
# .env 文件
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
```
