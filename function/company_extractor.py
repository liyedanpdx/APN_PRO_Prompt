#!/usr/bin/env python3
"""
公司关键词提取器
从岗位分析结果中提取推荐的目标公司列表，返回JSON格式
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.llm import LLMClient


class CompanyExtractor:
    """公司关键词提取器"""
    
    def __init__(self, model: str = "gemini-2.5-flash-lite", provider: str = "gemini"):
        """
        初始化提取器
        
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
        prompt_file = Path(__file__).parent.parent / "prompt" / "company_extractor_prompt.md"
        if prompt_file.exists():
            return prompt_file.read_text(encoding='utf-8')
        else:
            # 如果文件不存在，使用默认提示词
            return """
从以下岗位分析结果中提取推荐的目标公司名称，返回JSON格式：{"company": ["company1", "company2", ...]}

提取规则：
1. 查找"目标公司推荐"、"推荐公司"等章节
2. 提取表格或列表中的公司名称
3. 使用常用英文名称，中文公司可保留中文
4. 去除公司后缀（Inc., Ltd.等）
5. 如果没有找到公司，返回 {"company": []}

请严格按照JSON格式输出，不要添加任何额外文本。
"""
    
    def extract_companies(
        self, 
        analysis_result: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        从岗位分析结果中提取公司列表
        
        Args:
            analysis_result: 岗位分析的完整结果文本
            **kwargs: 额外的LLM参数
            
        Returns:
            包含提取结果的字典，格式：
            {
                "success": bool,
                "companies": List[str],
                "json_result": Dict,
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
                    "content": f"请从以下岗位分析结果中提取目标公司列表：\n\n{analysis_result}"
                }
            ]
            
            # 设置LLM参数
            llm_params = {
                "temperature": 0.1,  # 低温度确保稳定输出
                "max_tokens": 500,
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
                    "companies": [],
                    "json_result": {"company": []},
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
                    "companies": [],
                    "json_result": {"company": []},
                    "metadata": {
                        "provider": self.provider,
                        "model": self.model,
                        "duration": end_time - start_time
                    }
                }
            
            # 解析JSON结果
            json_result = self._parse_json_response(content)
            
            # 提取公司列表
            companies = json_result.get("company", [])
            
            return {
                "success": True,
                "companies": companies,
                "json_result": json_result,
                "raw_response": content.strip(),
                "metadata": {
                    "provider": self.provider,
                    "model": self.model,
                    "duration": end_time - start_time,
                    "company_count": len(companies),
                    "usage": response.get("data", {}).get("usage", {})
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"提取过程异常: {str(e)}",
                "companies": [],
                "json_result": {"company": []},
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
            json_pattern = r'\{[^{}]*"company"[^{}]*\[[^\]]*\][^{}]*\}'
            matches = re.findall(json_pattern, content, re.DOTALL)
            
            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    pass
            
            # 如果仍然无法解析，尝试提取公司名称
            company_names = self._extract_companies_from_text(content)
            return {"company": company_names}
    
    def _extract_companies_from_text(self, text: str) -> List[str]:
        """
        从文本中提取公司名称（备用方法）
        
        Args:
            text: 输入文本
            
        Returns:
            公司名称列表
        """
        import re
        
        companies = []
        
        # 常见的公司名称模式
        patterns = [
            r'"([^"]*)"',  # 双引号中的内容
            r"'([^']*)'",  # 单引号中的内容
            r'- ([^\n]+)',  # 以-开头的列表项
            r'• ([^\n]+)',  # 以•开头的列表项
            r'\d+\.\s*([^\n]+)',  # 数字列表项
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                cleaned = match.strip()
                if cleaned and len(cleaned) > 1:
                    companies.append(cleaned)
        
        # 去重并返回前10个
        return list(dict.fromkeys(companies))[:10]
    
    def save_result(self, result: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        保存提取结果到文件
        
        Args:
            result: 提取结果字典
            output_path: 输出文件路径，如果不指定则使用时间戳
            
        Returns:
            保存的文件路径
        """
        if not output_path:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"company_extraction_results_{timestamp}.json"
        
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
        print("用法: python company_extractor.py <analysis_result_file_or_text> [model] [provider]")
        print("示例: python company_extractor.py analysis_result.txt")
        print("示例: python company_extractor.py \"分析结果文本\" gemini-2.5-flash-lite gemini")
        sys.exit(1)
    
    # 解析命令行参数
    analysis_input = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "gemini-2.5-flash-lite"
    provider = sys.argv[3] if len(sys.argv) > 3 else "gemini"
    
    # 读取分析结果
    if Path(analysis_input).exists():
        # 如果是文件路径
        with open(analysis_input, 'r', encoding='utf-8') as f:
            analysis_result = f.read()
        print(f"📁 从文件读取分析结果: {analysis_input}")
    else:
        # 如果是直接文本
        analysis_result = analysis_input
        print("📝 使用直接输入的分析结果")
    
    print(f"🤖 使用模型: {provider} - {model}")
    print("=" * 60)
    
    # 创建提取器并执行提取
    extractor = CompanyExtractor(model=model, provider=provider)
    result = extractor.extract_companies(analysis_result)
    
    # 显示结果
    if result["success"]:
        print("✅ 公司提取成功")
        print(f"📊 提取到 {result['metadata']['company_count']} 家公司:")
        
        for i, company in enumerate(result["companies"], 1):
            print(f"  {i}. {company}")
        
        print(f"\n📋 JSON格式:")
        print(json.dumps(result["json_result"], ensure_ascii=False, indent=2))
        
        # 保存结果
        output_file = extractor.save_result(result)
        print(f"\n💾 结果已保存到: {output_file}")
        
        # 显示性能信息
        metadata = result["metadata"]
        print(f"\n⏱️ 性能信息:")
        print(f"  提取时间: {metadata['duration']:.2f}s")
        print(f"  提供商: {metadata['provider']}")
        print(f"  模型: {metadata['model']}")
        if "usage" in metadata and metadata["usage"]:
            usage = metadata["usage"]
            print(f"  Token使用: {usage}")
        
    else:
        print(f"❌ 公司提取失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()