import json
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.llm import LLMClient


class CandidateTagger:
    """
    候选人标签分析器
    用于分析职位描述或候选人搜索查询，判断是否包含特定的五个维度标准
    """
    
    def __init__(
        self, 
        model: str = "gpt-4-1106-preview", 
        provider: str = "openai",
        temperature: float = 0.1,
        max_tokens: int = 500,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ):
        """
        初始化候选人标签器
        
        Args:
            model: 使用的模型名称
            provider: LLM提供商 ("openai" 或 "perplexity")
            temperature: 温度参数 (0-2)，默认0.1确保一致性
            max_tokens: 最大token数，默认500
            top_p: 核采样参数 (0-1)，默认1.0
            frequency_penalty: 频率惩罚 (-2.0 to 2.0)，默认0.0
            presence_penalty: 存在惩罚 (-2.0 to 2.0)，默认0.0
        """
        self.llm_client = LLMClient()
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """
        从文件加载prompt模板
        
        Returns:
            prompt模板字符串
        """
        prompt_file = project_root / "prompt" / "candidate_tagger_prompt.md"
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # 如果文件不存在，返回基础的prompt
            return self._get_default_prompt()
        except Exception as e:
            print(f"Error loading prompt template: {e}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """
        获取默认的prompt模板
        
        Returns:
            默认prompt字符串
        """
        return """You are a professional candidate evaluation assistant. Analyze the given text and determine if it contains criteria for these 5 dimensions:

1. Location - Geographic requirements, office locations, remote work preferences
2. Job Title - Specific roles, positions, job functions, titles
3. Years of Experience - Experience requirements, seniority levels, years in field
4. Industry - Industry sectors, business domains, company types
5. Skills - Technical skills, soft skills, certifications, tools, technologies

Respond with valid JSON in this exact format:
{
    "result": [
        {"label": "Location", "containsCriteria": boolean},
        {"label": "Job Title", "containsCriteria": boolean},
        {"label": "Years of Experience", "containsCriteria": boolean},
        {"label": "Industry", "containsCriteria": boolean},
        {"label": "Skills", "containsCriteria": boolean}
    ]
}

Analyze this text:"""
    
    def analyze_text(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        分析文本并返回标签结果
        
        Args:
            text: 要分析的文本（职位描述或搜索查询）
            **kwargs: 传递给LLM的额外参数
            
        Returns:
            包含分析结果的字典
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Input text is empty",
                "result": None
            }
        
        # 构建完整的prompt
        full_prompt = f"{self.prompt_template}\n\n{text.strip()}"
        
        messages = [
            {
                "role": "user",
                "content": full_prompt
            }
        ]
        
        # 合并默认参数和传入参数
        llm_params = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            **kwargs  # 传入的参数会覆盖默认参数
        }
        
        try:
            # 调用LLM
            response = self.llm_client.call_llm(
                provider=self.provider,
                model=self.model,
                messages=messages,
                **llm_params
            )
            
            if not response.get("success"):
                return {
                    "success": False,
                    "error": f"LLM call failed: {response.get('error', 'Unknown error')}",
                    "result": None,
                    "raw_response": response
                }
            
            # 提取响应内容
            content = self.llm_client.get_response_content(response)
            if not content:
                return {
                    "success": False,
                    "error": "No content in LLM response",
                    "result": None,
                    "raw_response": response
                }
            
            # 解析JSON响应
            parsed_result = self._parse_llm_response(content)
            
            return {
                "success": True,
                "result": parsed_result,
                "raw_content": content,
                "usage": response.get("data", {}).get("usage", {}),
                "model_used": response.get("data", {}).get("model", self.model),
                "provider": self.provider
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "result": None
            }
    
    def _parse_llm_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析LLM返回的JSON响应
        
        Args:
            content: LLM返回的原始内容
            
        Returns:
            解析后的结果字典
        """
        # 尝试直接解析JSON
        try:
            # 移除可能的markdown代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            result = json.loads(content)
            
            # 验证响应格式
            if self._validate_response_format(result):
                return result
            else:
                raise ValueError("Invalid response format")
                
        except json.JSONDecodeError as e:
            # JSON解析失败时的处理
            print(f"JSON parsing failed: {e}")
            print(f"Content: {content}")
            return None
        except Exception as e:
            print(f"Response parsing failed: {e}")
            return None
    
    def _validate_response_format(self, result: Dict[str, Any]) -> bool:
        """
        验证响应格式是否正确
        
        Args:
            result: 解析后的结果字典
            
        Returns:
            是否格式正确
        """
        try:
            # 检查是否有result键
            if "result" not in result:
                return False
            
            result_list = result["result"]
            if not isinstance(result_list, list) or len(result_list) != 5:
                return False
            
            # 检查每个项目的格式
            expected_labels = ["Location", "Job Title", "Years of Experience", "Industry", "Skills"]
            
            for i, item in enumerate(result_list):
                if not isinstance(item, dict):
                    return False
                if "label" not in item or "containsCriteria" not in item:
                    return False
                if item["label"] != expected_labels[i]:
                    return False
                if not isinstance(item["containsCriteria"], bool):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def batch_analyze(self, texts: list[str], **kwargs) -> list[Dict[str, Any]]:
        """
        批量分析多个文本
        
        Args:
            texts: 要分析的文本列表
            **kwargs: 传递给LLM的额外参数
            
        Returns:
            分析结果列表
        """
        results = []
        for i, text in enumerate(texts):
            print(f"Analyzing text {i+1}/{len(texts)}...")
            result = self.analyze_text(text, **kwargs)
            results.append(result)
        
        return results
    
    def get_summary_stats(self, results: list[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取批量分析结果的统计信息
        
        Args:
            results: 分析结果列表
            
        Returns:
            统计信息字典
        """
        total = len(results)
        successful = sum(1 for r in results if r.get("success"))
        failed = total - successful
        
        # 统计每个维度的出现频率
        dimension_stats = {
            "Location": 0,
            "Job Title": 0, 
            "Years of Experience": 0,
            "Industry": 0,
            "Skills": 0
        }
        
        for result in results:
            if result.get("success") and result.get("result"):
                for item in result["result"]["result"]:
                    if item.get("containsCriteria"):
                        dimension_stats[item["label"]] += 1
        
        return {
            "total_analyzed": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "dimension_frequencies": dimension_stats,
            "dimension_percentages": {
                k: v / successful * 100 if successful > 0 else 0 
                for k, v in dimension_stats.items()
            }
        }


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("Usage: python candidate_tagger.py \"text to analyze\"")
        sys.exit(1)
    
    # 获取输入文本
    text = sys.argv[1]
    
    # 创建标签器实例 - 使用nano模型，temperature=0
    # tagger = CandidateTagger(
    #     model="gpt-4.1-nano-2025-04-14",
    #     provider="openai", 
    #     temperature=0.0,
    #     max_tokens=500
    # )
    tagger = CandidateTagger(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        provider="groq", 
        temperature=0.0,
        max_tokens=500
    )
    
    
    # 分析文本
    text="We are looking for a backend engineer for our financial department. We hope this candidate have more than 5 years Remote"
    print(f"Analyzing: {text}")
    print("-" * 50)
    
    result = tagger.analyze_text(text)
    
    # 输出结果
    if result["success"]:
        print("✅ Analysis successful!")
        print("\nResult:")
        print(json.dumps(result["result"], indent=2, ensure_ascii=False))
        
        if "usage" in result:
            usage = result["usage"]
            print(f"\n📊 Usage Statistics:")
            print(f"  Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  Total tokens: {usage.get('total_tokens', 'N/A')}")
        
        print(f"\n🤖 Model: {result.get('model_used', 'N/A')}")
        print(f"🔧 Provider: {result.get('provider', 'N/A')}")
        
    else:
        print("❌ Analysis failed!")
        print(f"Error: {result['error']}")
        if "raw_response" in result:
            print(f"Raw response: {result['raw_response']}")

