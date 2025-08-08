import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import re
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.llm import LLMClient


class SourcingKeywordExtractor:
    """
    寻访关键词提取器
    用于从寻访策略结果中提取用于搜索的关键词，统一输出为英文格式
    """
    
    def __init__(
        self, 
        model: str = "gemini-2.5-flash-lite", 
        provider: str = "gemini",
        temperature: float = 0.1,  # 低温度确保结构化输出稳定
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ):
        """
        初始化寻访关键词提取器
        
        Args:
            model: 使用的模型名称
            provider: LLM提供商 ("openai", "gemini", "ali", "groq", "perplexity")
            temperature: 温度参数，默认0.1确保结构化输出稳定
            max_tokens: 最大token数，默认2000
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
        prompt_file = project_root / "prompt" / "sourcing_keyword_extractor_prompt.md"
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt file not found at {prompt_file}")
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
        return """You are a professional talent acquisition specialist. 
Extract searchable keywords from the provided sourcing plan result for talent hunting purposes.
Return the keywords in English JSON format: {"sourcing_keywords": ["keyword1", "keyword2", ...]}"""
    
    def _parse_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析JSON响应，支持多种格式
        
        Args:
            content: 响应内容
            
        Returns:
            解析后的JSON字典，如果失败返回None
        """
        # 清理内容
        content = content.strip()
        
        # 尝试多种JSON解析策略
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # ```json {} ```
            r'```\s*(\{.*?\})\s*```',      # ``` {} ```
            r'(\{.*?\})',                  # 直接的JSON对象
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict) and "sourcing_keywords" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        # 如果没有找到完整JSON，尝试提取关键词列表
        try:
            # 查找类似 ["keyword1", "keyword2"] 的模式
            list_pattern = r'\[([^\]]*)\]'
            matches = re.findall(list_pattern, content)
            
            for match in matches:
                # 提取引号内的内容
                keywords = re.findall(r'"([^"]*)"', match)
                if keywords:
                    return {"sourcing_keywords": keywords}
                    
                # 尝试逗号分割
                keywords = [k.strip().strip('"\'') for k in match.split(',')]
                keywords = [k for k in keywords if k and len(k) > 1]
                if keywords:
                    return {"sourcing_keywords": keywords}
                    
        except Exception as e:
            print(f"Error in fallback parsing: {e}")
        
        return None
    
    def extract_sourcing_keywords(
        self, 
        sourcing_plan_content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        从寻访策略内容中提取关键词
        
        Args:
            sourcing_plan_content: 寻访策略内容
            **kwargs: 传递给LLM的额外参数
            
        Returns:
            包含提取结果的字典
        """
        # 验证输入
        if not sourcing_plan_content or not sourcing_plan_content.strip():
            return {
                "success": False,
                "error": "Sourcing plan content is empty",
                "keywords": [],
                "json_result": None
            }
        
        # 构建完整的prompt
        full_prompt = f"""{self.prompt_template}

## Sourcing Plan Content:

{sourcing_plan_content.strip()}

Please extract the most relevant keywords for talent searching and return them in the required JSON format."""
        
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
                    "keywords": [],
                    "json_result": None,
                    "raw_response": response
                }
            
            # 提取响应内容
            content = self.llm_client.get_response_content(response)
            if not content:
                return {
                    "success": False,
                    "error": "No content in LLM response",
                    "keywords": [],
                    "json_result": None,
                    "raw_response": response
                }
            
            # 解析JSON响应
            parsed_result = self._parse_json_response(content)
            if not parsed_result:
                return {
                    "success": False,
                    "error": "Failed to parse JSON response",
                    "keywords": [],
                    "json_result": None,
                    "raw_content": content
                }
            
            # 提取关键词列表
            keywords = parsed_result.get("sourcing_keywords", [])
            if not isinstance(keywords, list):
                keywords = []
            
            # 清理和验证关键词
            clean_keywords = []
            for keyword in keywords:
                if isinstance(keyword, str) and len(keyword.strip()) > 0:
                    clean_keywords.append(keyword.strip())
            
            return {
                "success": True,
                "keywords": clean_keywords,
                "json_result": {"sourcing_keywords": clean_keywords},
                "raw_content": content,
                "usage": response.get("data", {}).get("usage", {}),
                "model_used": response.get("data", {}).get("model", self.model),
                "provider": self.provider
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Keyword extraction failed: {str(e)}",
                "keywords": [],
                "json_result": None
            }
    
    def save_keywords(
        self, 
        result: Dict[str, Any], 
        output_file: Optional[str] = None
    ) -> str:
        """
        保存关键词结果到文件
        
        Args:
            result: 关键词提取结果
            output_file: 输出文件路径，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        if not output_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"sourcing_keywords_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if result.get("success"):
                    json.dump(result["json_result"], f, ensure_ascii=False, indent=2)
                else:
                    json.dump({
                        "success": False,
                        "error": result.get("error", "Unknown error"),
                        "sourcing_keywords": []
                    }, f, ensure_ascii=False, indent=2)
            
            return output_file
            
        except Exception as e:
            print(f"Failed to save keywords to file: {e}")
            return None
    
    def get_supported_providers(self) -> List[str]:
        """
        获取支持的LLM提供商列表
        
        Returns:
            支持的提供商列表
        """
        return ["openai", "gemini", "ali", "groq", "perplexity"]
    
    def get_recommended_models(self, provider: str) -> List[str]:
        """
        获取推荐的模型列表
        
        Args:
            provider: 提供商名称
            
        Returns:
            推荐的模型列表
        """
        models = {
            "openai": ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo"],
            "gemini": ["gemini-2.5-flash-lite", "gemini-1.5-pro", "gemini-1.5-flash"],
            "ali": ["deepseek-v3", "qwen-max", "qwen-turbo", "qwen-plus"],
            "groq": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            "perplexity": ["llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online"]
        }
        
        return models.get(provider.lower(), [])


if __name__ == "__main__":
    # 中文寻访策略测试案例
    sourcing_plan_cn = """
    # 岗位定位解析
    
    **核心价值**  
    该岗位负责腾讯会议产品的持续优化与商业化策略制定，解决用户增长、体验提升及商业变现的关键问题。
    
    # 寻访策略设计
    
    ## 精准渠道
    
    | 渠道类型 | 渠道 |
    |---------|------|
    | 同业挖猎 | 阿里云、字节跳动、华为云、钉钉、Zoom |
    | 专业社区 | 知乎、人人都是产品经理、PMCAFF |
    
    ## 关键词矩阵
    
    | 寻访阶段 | 关键词组合示例 |
    |---------|---------------|
    | 初期广撒网 | 在线办公 + 产品策划 + 用户增长 + 数据分析 |
    | 中期精准挖猎 | 企业协作 + 视频会议 + 商业化 + 用户调研 |
    | 后期攻坚 | 0-1 产品搭建 + 千万级用户运营 + 商业模式设计 |
    """
    
    # 英文寻访策略测试案例
    sourcing_plan_en = """
    # Position Analysis
    
    **Core Value**  
    This role is responsible for backend system architecture and scalability optimization for social media platforms.
    
    # Sourcing Strategy Design
    
    ## Precise Channels
    
    | Channel Type | Specific Channels |
    |-------------|-------------------|
    | Industry Hunting | Meta, Google, Twitter, TikTok, Snapchat |
    | Professional Communities | GitHub, Stack Overflow, Reddit |
    
    ## Keyword Matrix
    
    | Sourcing Phase | Keyword Combinations |
    |---------------|---------------------|
    | Initial Broad Search | backend development + distributed systems + scalability + performance |
    | Mid-stage Precision | microservices + API design + database optimization + cloud architecture |
    | Final Focused Hunt | system design + high concurrency + real-time processing + technical leadership |
    """
    
    # 创建提取器实例
    extractor = SourcingKeywordExtractor(
        model="gemini-2.5-flash-lite",
        provider="gemini",
        temperature=0.1,
        max_tokens=2000
    )
    
    # 测试中文案例
    print("=" * 80)
    print("🇨🇳 中文寻访策略关键词提取测试")
    print("=" * 80)
    print("🔄 Extracting keywords...")
    
    result_cn = extractor.extract_sourcing_keywords(sourcing_plan_cn)
    
    if result_cn["success"]:
        print("✅ Extraction successful!")
        print(f"📋 Extracted Keywords ({len(result_cn['keywords'])} total):")
        for i, keyword in enumerate(result_cn['keywords'], 1):
            print(f"  {i}. {keyword}")
        print(f"\n🔤 JSON Result:")
        print(json.dumps(result_cn['json_result'], ensure_ascii=False, indent=2))
    else:
        print("❌ Extraction failed!")
        print(f"Error: {result_cn['error']}")
    
    print("\n" + "=" * 80)
    print("🇺🇸 英文寻访策略关键词提取测试")
    print("=" * 80)
    print("🔄 Extracting keywords...")
    
    # 测试英文案例
    result_en = extractor.extract_sourcing_keywords(sourcing_plan_en)
    
    if result_en["success"]:
        print("✅ Extraction successful!")
        print(f"📋 Extracted Keywords ({len(result_en['keywords'])} total):")
        for i, keyword in enumerate(result_en['keywords'], 1):
            print(f"  {i}. {keyword}")
        print(f"\n🔤 JSON Result:")
        print(json.dumps(result_en['json_result'], ensure_ascii=False, indent=2))
    else:
        print("❌ Extraction failed!")
        print(f"Error: {result_en['error']}")
    
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    print(f"中文测试: {'✅' if result_cn['success'] else '❌'}")
    print(f"英文测试: {'✅' if result_en['success'] else '❌'}")
    
    # 保存结果示例
    if result_cn["success"]:
        output_file = extractor.save_keywords(result_cn)
        if output_file:
            print(f"\n💾 Keywords saved to: {output_file}")