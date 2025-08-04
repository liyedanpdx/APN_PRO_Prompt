# APN Pro AI 项目开发记录

## 候选人标签器准确性测试增强 (2025-01-31)

### 功能概述
为 `candidate_tagger_test.py` 增加了准确性测试功能，可以评估不同LLM模型在5类维度分类任务上的表现。

### 核心改进

#### 1. 标准答案（Ground Truth）生成
- **位置**: `_generate_ground_truth()` 方法
- **功能**: 为50个测试样本手工标注了5个维度的正确答案
- **维度**: Location, Job Title, Years of Experience, Industry, Skills
- **格式**: 每个样本对应一个字典，键为维度名，值为布尔值

```python
def _generate_ground_truth(self) -> List[Dict[str, bool]]:
    return [
        # "We are looking for a backend engineer..."
        {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": True, "Skills": False},
        # ... 50个样本的标注
    ]
```

#### 2. 准确性指标计算
- **位置**: `_calculate_accuracy_metrics()` 方法
- **指标类型**:
  - 总体准确率 (Overall Accuracy)
  - 各维度准确率、精确率、召回率、F1分数
  - 混淆矩阵统计 (TP, FP, TN, FN)

#### 3. 测试结果增强
- **配置信息扩展**: 添加模型名称、提供商、标准答案样本数
- **准确性报告**: 在测试结果中新增准确性指标显示
- **JSON保存**: 保存的结果文件包含完整的准确性分析

### 测试样本分析
总共50个测试样本，涵盖：
- **完整职位描述** (30个): 包含多个维度信息
- **简短查询** (10个): 测试单一维度识别
- **复杂场景** (10个): 测试边界情况和组合维度

### 支持的LLM提供商
- **OpenAI**: gpt-4.1-nano-2025-04-14
- **Gemini**: gemini-2.5-flash-lite, gemini-1.5-pro/flash
- **Alibaba**: deepseek-v3, qwen系列
- **Groq**: llama-3.1-70b-versatile等
- **Perplexity**: llama-3.1-sonar系列

### 测试输出示例
```
🎯 准确性指标:
  总体准确率: 85.2%
  正确预测数: 213
  总预测数: 250

📊 各维度详细指标:
  Location:
    准确率: 88.0%
    精确率: 82.5%
    召回率: 91.2%
    F1分数: 0.866
```

### 使用方法
1. **运行标准测试**:
   ```bash
   python test/candidate_tagger_test.py
   ```

2. **自定义配置**:
   ```python
   PROVIDER = "gemini"  # 切换提供商
   MODEL = "gemini-2.5-flash-lite"  # 选择模型
   TOTAL_SAMPLES = 50  # 设置样本数
   ```

3. **结果文件**: 自动保存为 `performance_test_results_YYYYMMDD_HHMMSS.json`

### 技术细节
- **并发测试**: 支持可调节的并发限制
- **错误处理**: 完善的异常处理和错误统计
- **统计分析**: 时间、Token使用、维度频率等全方位统计
- **准确性评估**: 基于人工标注的标准答案进行客观评估

### 应用价值
1. **模型选择**: 帮助选择最适合的LLM提供商和模型
2. **性能监控**: 跟踪模型在特定任务上的表现变化
3. **质量保证**: 确保候选人标签器的准确性和稳定性
4. **成本优化**: 在准确性和成本之间找到最佳平衡点

---

*最后更新: 2025-01-31*