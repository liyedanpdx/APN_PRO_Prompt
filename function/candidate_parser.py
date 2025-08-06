#!/usr/bin/env python3
"""
候选人描述解析器
将用户描述的理想候选人转化为结构化的JSON格式
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import time
import re

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.llm import LLMClient


class CandidateParser:
    """候选人描述解析器"""
    
    def __init__(self, model: str = "gemini-2.5-flash-lite", provider: str = "gemini"):
        """
        初始化解析器
        
        Args:
            model: LLM模型名称
            provider: LLM提供商
        """
        self.model = model
        self.provider = provider
        self.llm_client = LLMClient()
        
        # 读取提示词模板
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """加载提示词模板"""
        prompt_file = Path(__file__).parent.parent / "prompt" / "candidate_parser_prompt.md"
        if prompt_file.exists():
            return prompt_file.read_text(encoding='utf-8')
        else:
            # 如果文件不存在，使用简化的默认提示词
            return """
Parse the candidate description and return JSON format:
{
  "jobTitles": ["engineer"],
  "requiredSkills": ["JavaScript"],
  "preferredSkills": ["AWS"],
  "industry": ["Technology"],
  "Location": ["San Francisco, CA, USA"],
  "Experience": {"gte": 1, "lte": 3},
  "Keywords": ["other important terms"]
}

Convert all content to English. Return only the JSON object.
"""
    
    def parse_candidate_description(
        self, 
        description: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        解析候选人描述
        
        Args:
            description: 候选人描述文本
            **kwargs: 额外的LLM参数
            
        Returns:
            包含解析结果的字典，格式：
            {
                "success": bool,
                "parsed_data": Dict,
                "raw_response": str,
                "metadata": Dict
            }
        """
        try:
            # 构建消息
            messages = [
                {
                    "role": "system", 
                    "content": self.prompt_template
                },
                {
                    "role": "user", 
                    "content": f"Parse this candidate description:\n\n{description}"
                }
            ]
            
            # 设置LLM参数
            llm_params = {
                "temperature": 0.1,  # 低温度确保结构化输出
                "max_tokens": 800,
                **kwargs
            }
            
            # 调用LLM
            start_time = time.time()
            response = self.llm_client.call_llm(
                provider=self.provider,
                model=self.model,
                messages=messages,
                **llm_params
            )
            end_time = time.time()
            
            if not response.get("success"):
                return {
                    "success": False,
                    "error": response.get("error", "LLM调用失败"),
                    "parsed_data": self._get_empty_structure(),
                    "metadata": {
                        "provider": self.provider,
                        "model": self.model,
                        "duration": end_time - start_time
                    }
                }
            
            # 提取响应内容
            content = self.llm_client.get_response_content(response)
            if not content:
                return {
                    "success": False,
                    "error": "LLM返回空内容",
                    "parsed_data": self._get_empty_structure(),
                    "metadata": {
                        "provider": self.provider,
                        "model": self.model,
                        "duration": end_time - start_time
                    }
                }
            
            # 解析JSON结果
            parsed_data = self._parse_json_response(content)
            
            # 验证和清理数据
            validated_data = self._validate_and_clean_data(parsed_data)
            
            return {
                "success": True,
                "parsed_data": validated_data,
                "raw_response": content.strip(),
                "metadata": {
                    "provider": self.provider,
                    "model": self.model,
                    "duration": end_time - start_time,
                    "usage": response.get("data", {}).get("usage", {}),
                    "field_counts": {
                        "jobTitles": len(validated_data.get("jobTitles", [])),
                        "requiredSkills": len(validated_data.get("requiredSkills", [])),
                        "preferredSkills": len(validated_data.get("preferredSkills", [])),
                        "industry": len(validated_data.get("industry", [])),
                        "Location": len(validated_data.get("Location", [])),
                        "Keywords": len(validated_data.get("Keywords", []))
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"解析过程异常: {str(e)}",
                "parsed_data": self._get_empty_structure(),
                "metadata": {
                    "provider": self.provider,
                    "model": self.model
                }
            }
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        解析LLM返回的JSON响应
        
        Args:
            content: LLM返回的原始内容
            
        Returns:
            解析后的JSON对象
        """
        try:
            # 尝试直接解析
            return json.loads(content.strip())
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            import re
            
            # 查找JSON格式的内容
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, content)
            
            if matches:
                try:
                    # 尝试解析最大的JSON块
                    longest_match = max(matches, key=len)
                    return json.loads(longest_match)
                except json.JSONDecodeError:
                    pass
            
            # 如果仍然无法解析，尝试手动构建
            return self._manual_parse_response(content)
    
    def _manual_parse_response(self, content: str) -> Dict[str, Any]:
        """
        手动解析响应内容（备用方法）
        
        Args:
            content: 响应内容
            
        Returns:
            解析后的数据结构
        """
        result = self._get_empty_structure()
        
        # 简单的正则模式提取
        patterns = {
            "jobTitles": r'"jobTitles":\s*\[(.*?)\]',
            "requiredSkills": r'"requiredSkills":\s*\[(.*?)\]',
            "preferredSkills": r'"preferredSkills":\s*\[(.*?)\]',
            "industry": r'"industry":\s*\[(.*?)\]',
            "Location": r'"Location":\s*\[(.*?)\]',
            "Keywords": r'"Keywords":\s*\[(.*?)\]'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                items_str = match.group(1)
                # 提取引号中的内容
                items = re.findall(r'"([^"]*)"', items_str)
                result[field] = items
        
        # 处理Experience字段
        exp_pattern = r'"Experience":\s*\{[^}]*"gte":\s*(\d+|null)[^}]*"lte":\s*(\d+|null)[^}]*\}'
        exp_match = re.search(exp_pattern, content)
        if exp_match:
            gte_str, lte_str = exp_match.groups()
            result["Experience"] = {
                "gte": int(gte_str) if gte_str != "null" else None,
                "lte": int(lte_str) if lte_str != "null" else None
            }
        
        return result
    
    def _get_empty_structure(self) -> Dict[str, Any]:
        """获取空的数据结构"""
        return {
            "jobTitles": [],
            "requiredSkills": [],
            "preferredSkills": [],
            "industry": [],
            "Location": [],
            "Experience": {"gte": None, "lte": None},
            "Keywords": []
        }
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证和清理数据
        
        Args:
            data: 原始解析数据
            
        Returns:
            清理后的数据
        """
        result = self._get_empty_structure()
        
        # 验证和清理数组字段
        array_fields = ["jobTitles", "requiredSkills", "preferredSkills", "industry", "Location", "Keywords"]
        for field in array_fields:
            if field in data and isinstance(data[field], list):
                # 过滤空值和非字符串值
                cleaned_list = [
                    str(item).strip() 
                    for item in data[field] 
                    if item and str(item).strip()
                ]
                result[field] = cleaned_list[:10]  # 限制最多10个项目
        
        # 验证Experience字段
        if "Experience" in data and isinstance(data["Experience"], dict):
            exp = data["Experience"]
            result["Experience"] = {
                "gte": self._safe_int_conversion(exp.get("gte")),
                "lte": self._safe_int_conversion(exp.get("lte"))
            }
        
        # 验证industry字段是否在预定义列表中
        if result["industry"]:
            valid_industries = self._get_valid_industries()
            result["industry"] = [
                industry for industry in result["industry"] 
                if industry in valid_industries
            ]
        
        return result
    
    def _safe_int_conversion(self, value: Any) -> Optional[int]:
        """安全的整数转换"""
        if value is None or value == "null":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _get_valid_industries(self) -> List[str]:
        """获取有效的行业列表"""
        return [
            "Technology", "Software", "Financial Services", "Healthcare", "E-commerce",
            "Manufacturing", "Consulting", "Education", "Media & Entertainment", "Telecommunications",
            "Automotive", "Aerospace", "Biotechnology", "Real Estate", "Energy",
            "Retail", "Transportation", "Food & Beverage", "Pharmaceutical", "Construction",
            "Agriculture", "Gaming", "Fintech", "AI & Machine Learning", "Cybersecurity",
            "Cloud Services", "Mobile Development", "Web Development", "Data Analytics", "DevOps",
            "Digital Marketing", "UX/UI Design", "Blockchain", "IoT", "Robotics",
            "Virtual Reality", "Augmented Reality", "SaaS", "Enterprise Software", "Government",
            "Non-profit", "Sports & Fitness", "Travel & Tourism", "Fashion", "Beauty & Cosmetics",
            "Legal Services", "Architecture", "Logistics", "Insurance", "Banking",
            "Investment", "Trading"
        ]
    
    def save_result(self, result: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        保存解析结果到文件
        
        Args:
            result: 解析结果字典
            output_path: 输出文件路径，如果不指定则使用时间戳
            
        Returns:
            保存的文件路径
        """
        if not output_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"candidate_parsing_results_{timestamp}.json"
        
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return str(output_file)


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python candidate_parser.py <candidate_description> [model] [provider]")
        print("示例: python candidate_parser.py \"需要一个前端工程师，会React\"")
        print("示例: python candidate_parser.py \"Looking for senior engineer\" gpt-4 openai")
        sys.exit(1)
    
    # 解析命令行参数
    description = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "gemini-2.5-flash-lite"
    provider = sys.argv[3] if len(sys.argv) > 3 else "gemini"
    
    print(f"🔍 解析候选人描述: {description}")
    print(f"🤖 使用模型: {provider} - {model}")
    print("=" * 80)
    
    # 创建解析器并执行解析
    parser = CandidateParser(model=model, provider=provider)
    result = parser.parse_candidate_description(description)
    
    # 显示结果
    if result["success"]:
        print("✅ 解析成功")
        
        parsed_data = result["parsed_data"]
        
        print(f"\n📋 解析结果:")
        print(f"  职位标题: {parsed_data['jobTitles']}")
        print(f"  必需技能: {parsed_data['requiredSkills']}")
        print(f"  优选技能: {parsed_data['preferredSkills']}")
        print(f"  行业: {parsed_data['industry']}")
        print(f"  地点: {parsed_data['Location']}")
        print(f"  经验要求: {parsed_data['Experience']}")
        print(f"  关键词: {parsed_data['Keywords']}")
        
        print(f"\n🔧 标准JSON格式:")
        print(json.dumps(parsed_data, ensure_ascii=False, indent=2))
        
        # 保存结果
        output_file = parser.save_result(result)
        print(f"\n💾 结果已保存到: {output_file}")
        
        # 显示性能信息
        metadata = result["metadata"]
        print(f"\n⏱️ 性能信息:")
        print(f"  解析时间: {metadata['duration']:.2f}s")
        print(f"  提供商: {metadata['provider']}")
        print(f"  模型: {metadata['model']}")
        print(f"  字段统计: {metadata.get('field_counts', {})}")
        if "usage" in metadata and metadata["usage"]:
            usage = metadata["usage"]
            print(f"  Token使用: {usage}")
        
    else:
        print(f"❌ 解析失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()