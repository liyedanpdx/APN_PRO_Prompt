# 公司关键词提取提示词

## 任务描述
从岗位分析结果中提取推荐的目标公司名称，返回JSON格式的公司列表。

## 输入内容
岗位分析的完整结果文本，其中包含了目标公司推荐信息。

## 输出要求
1. 仅提取公司名称，不包含其他信息
2. 公司名称使用英文或原文名称
3. 返回标准JSON格式：`{"company": ["company1", "company2", ...]}`
4. 如果没有找到公司信息，返回空数组：`{"company": []}`

## 提取规则
1. **识别公司推荐部分**: 查找包含"目标公司推荐"、"推荐公司"、"target companies"等关键词的章节
2. **提取公司名称**: 
   - 提取表格中的公司名称
   - 提取列表中的公司名称
   - 提取正文中明确提到的公司名称
3. **标准化处理**:
   - 使用公司的常用英文名称（如：Apple, Google, Microsoft）
   - 如果是中文公司，可保留中文名称（如：阿里巴巴, 腾讯）
   - 去除公司后缀（如：Inc., Ltd., Corporation等）
4. **去重处理**: 确保列表中没有重复的公司名称

## 示例

### 输入示例1:
```
## 目标公司推荐表格

| 公司名称 | 业务相似度 | 产品策略匹配度 |
|----------|------------|------------------|
| 腾讯 | 高 | 高 |
| 字节跳动 | 中等 | 高 |  
| 阿里巴巴 | 中等 | 中等 |
| 美团 | 高 | 高 |
```

### 输出示例1:
```json
{"company": ["腾讯", "字节跳动", "阿里巴巴", "美团"]}
```

### 输入示例2:
```
Based on the analysis, I recommend targeting the following companies:
- Apple Inc. for their focus on user experience
- Google LLC for their product innovation approach  
- Microsoft Corporation for their enterprise solutions
- Amazon for their customer-centric strategy
```

### 输出示例2:
```json
{"company": ["Apple", "Google", "Microsoft", "Amazon"]}
```

### 输入示例3:
```
这是一个岗位分析结果，但没有包含具体的公司推荐信息。
```

### 输出示例3:
```json
{"company": []}
```

## 注意事项
1. 严格按照JSON格式输出，不要添加任何额外的文本
2. 确保JSON格式正确，可以被标准JSON解析器解析
3. 公司名称保持简洁，去除不必要的法律实体后缀
4. 如果文本中没有明确的公司推荐，返回空数组