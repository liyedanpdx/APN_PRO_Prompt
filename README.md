# APN Pro AI - 候选人标签分析系统

这是一个基于OpenAI和Perplexity API的候选人标签分析系统，能够分析职位描述或候选人搜索查询，判断是否包含5个关键维度的标准。

## 项目结构

```
APN Pro AI/
├── api/
│   └── llm.py                 # 统一LLM调用接口
├── function/
│   └── candidate_tagger.py    # 候选人标签分析器
├── prompt/
│   └── candidate_tagger_prompt.md  # Prompt模板
├── test/                      # 测试文件
├── config.py                  # 配置管理
├── .env                       # 环境变量配置
├── requirements.txt           # 依赖包列表
├── example_usage.py           # 使用示例
└── README.md                  # 项目说明
```

## 功能特性

### 5个分析维度

1. **Location (位置)** - 地理要求、办公地点、远程工作偏好
2. **Job Title (职位)** - 具体角色、职位、工作职能、头衔
3. **Years of Experience (工作经验)** - 经验要求、资历级别、从业年限
4. **Industry (行业)** - 行业领域、业务域、公司类型
5. **Skills (技能)** - 技术技能、软技能、认证、工具、技术

### LLM支持

- **OpenAI**: GPT-4, GPT-3.5-turbo 等
- **Perplexity**: Llama-3.1-sonar 系列模型

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `.env` 文件，添加你的API密钥：

```env
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_DEFAULT_MODEL=gpt-4-1106-preview

# Perplexity配置  
PERPLEXITY_API_KEY=your_perplexity_api_key_here
PERPLEXITY_DEFAULT_MODEL=llama-3.1-sonar-small-128k-online

# 通用配置
DEFAULT_PROVIDER=openai
```

## 使用方法

### 基本使用

```python
from function.candidate_tagger import CandidateTagger

# 创建标签器实例
tagger = CandidateTagger(
    model="gpt-4-1106-preview",
    provider="openai"
)

# 分析文本
text = "We are looking for a backend engineer for our financial department. We hope this candidate have more than 5 years"
result = tagger.analyze_text(text)

if result["success"]:
    print(result["result"])
```

### 命令行使用

```bash
python function/candidate_tagger.py "要分析的文本"
```

### 批量分析

```python
texts = [
    "Looking for Python developers in New York",
    "Senior data scientist needed",
    # 更多文本...
]

results = tagger.batch_analyze(texts)
stats = tagger.get_summary_stats(results)
```

## 输出格式

系统返回标准的JSON格式：

```json
{
    "result": [
        {
            "label": "Location",
            "containsCriteria": false
        },
        {
            "label": "Job Title", 
            "containsCriteria": true
        },
        {
            "label": "Years of Experience",
            "containsCriteria": true
        },
        {
            "label": "Industry",
            "containsCriteria": true
        },
        {
            "label": "Skills",
            "containsCriteria": false
        }
    ]
}
```

## 示例

运行示例程序：

```bash
python example_usage.py
```

## API配置参数

### OpenAI参数
- `model`: 模型名称
- `temperature`: 温度参数 (0-2)
- `max_tokens`: 最大token数
- `top_p`: 核采样参数
- `frequency_penalty`: 频率惩罚
- `presence_penalty`: 存在惩罚

### Perplexity参数
- `model`: 模型名称
- `temperature`: 温度参数 (0-2) 
- `max_tokens`: 最大token数
- `top_p`: 核采样参数
- `top_k`: top-k采样参数
- `frequency_penalty`: 频率惩罚
- `presence_penalty`: 存在惩罚

## 注意事项

1. 确保API密钥格式正确：
   - OpenAI: 以 `sk-` 开头
   - Perplexity: 以 `pplx-` 开头

2. 分析结果基于AI模型判断，可能存在主观性

3. 建议使用低温度参数 (0.1-0.3) 以确保结果一致性

## 许可证

本项目仅用于学习和研究目的。