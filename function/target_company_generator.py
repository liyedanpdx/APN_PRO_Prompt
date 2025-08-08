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


class JobAnalyzer:
    """
    岗位分析器
    用于分析职位描述、公司名称和岗位标题，提供业务模式分析和目标公司推荐
    """
    
    def __init__(
        self, 
        model: str = "gpt-4-1106-preview", 
        provider: str = "openai",
        temperature: float = 0.3,
        max_tokens: int = 4000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0
    ):
        """
        初始化岗位分析器
        
        Args:
            model: 使用的模型名称
            provider: LLM提供商 ("openai", "gemini", "ali", "groq", "perplexity")
            temperature: 温度参数 (0-2)，默认0.3确保创意性分析
            max_tokens: 最大token数，默认4000支持长篇分析
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
        prompt_file = project_root / "prompt" / "target_company_generator_prompt.md"
        
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
        return """You are a professional HR analyst and business intelligence expert. 
Analyze the provided job position and company information, then provide comprehensive business model analysis 
and target company recommendations for talent acquisition.

Please provide your analysis in a structured format covering:
1. Business Model Analysis
2. Position Analysis  
3. Target Company Recommendations

Detect the input language and respond in the same language (Chinese or English)."""
    
    def _detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 要检测的文本
            
        Returns:
            语言类型 ("chinese" 或 "english")
        """
        # 简单的中文字符检测
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        total_chars = len(re.sub(r'\s', '', text))
        
        if total_chars == 0:
            return "english"
        
        chinese_ratio = chinese_chars / total_chars
        return "chinese" if chinese_ratio > 0.3 else "english"
    
    def analyze_job(
        self, 
        jd_content: str, 
        company_name: str, 
        position_title: str,
        output_language: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        分析岗位并返回分析结果
        
        Args:
            jd_content: 职位描述内容
            company_name: 公司名称
            position_title: 岗位标题
            output_language: 输出语言 ("auto", "chinese", "english")
            **kwargs: 传递给LLM的额外参数
            
        Returns:
            包含分析结果的字典
        """
        # 验证输入
        if not jd_content or not jd_content.strip():
            return {
                "success": False,
                "error": "Job description content is empty",
                "result": None
            }
        
        if not company_name or not company_name.strip():
            return {
                "success": False,
                "error": "Company name is empty",
                "result": None
            }
        
        if not position_title or not position_title.strip():
            return {
                "success": False,
                "error": "Position title is empty", 
                "result": None
            }
        
        # 确定输出语言
        if output_language == "auto":
            combined_text = f"{jd_content} {company_name} {position_title}"
            detected_language = self._detect_language(combined_text)
        else:
            detected_language = output_language.lower()
        
        # 根据语言设置添加语言指定指令
        language_instruction = ""
        if detected_language == "chinese":
            language_instruction = "\n\nIMPORTANT: Please respond in Chinese (中文)."
        elif detected_language == "english":
            language_instruction = "\n\nIMPORTANT: Please respond in English."
        
        # 构建完整的prompt
        full_prompt = f"""{self.prompt_template}

## Input Information

**JD Content (职位描述):**
{jd_content.strip()}

**Company Name (公司名称):**
{company_name.strip()}

**Position Title (岗位标题):**
{position_title.strip()}

Please analyze this job position following the framework provided above.{language_instruction}"""
        
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
            
            return {
                "success": True,
                "result": {
                    "analysis": content,
                    "input_info": {
                        "jd_content": jd_content,
                        "company_name": company_name,
                        "position_title": position_title
                    },
                    "detected_language": detected_language
                },
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
    
    def save_analysis_result(
        self, 
        result: Dict[str, Any], 
        output_file: Optional[str] = None
    ) -> str:
        """
        保存分析结果到文件
        
        Args:
            result: 分析结果
            output_file: 输出文件路径，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        if not output_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"job_analysis_result_{timestamp}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if result.get("success"):
                    # 写入分析结果
                    f.write("=" * 80 + "\n")
                    f.write("JOB ANALYSIS RESULT\n")
                    f.write("=" * 80 + "\n\n")
                    
                    # 输入信息
                    input_info = result["result"]["input_info"]
                    f.write("INPUT INFORMATION:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Company: {input_info['company_name']}\n")
                    f.write(f"Position: {input_info['position_title']}\n")
                    f.write(f"Language: {result['result']['detected_language']}\n")
                    f.write(f"Model: {result.get('model_used', 'N/A')}\n")
                    f.write(f"Provider: {result.get('provider', 'N/A')}\n\n")
                    
                    # JD内容
                    f.write("JOB DESCRIPTION:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{input_info['jd_content']}\n\n")
                    
                    # 分析结果
                    f.write("ANALYSIS RESULT:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{result['result']['analysis']}\n\n")
                    
                    # 使用统计
                    if result.get("usage"):
                        usage = result["usage"]
                        f.write("USAGE STATISTICS:\n")
                        f.write("-" * 40 + "\n")
                        f.write(f"Prompt tokens: {usage.get('prompt_tokens', 'N/A')}\n")
                        f.write(f"Completion tokens: {usage.get('completion_tokens', 'N/A')}\n")
                        f.write(f"Total tokens: {usage.get('total_tokens', 'N/A')}\n")
                    
                else:
                    f.write("ANALYSIS FAILED\n")
                    f.write("=" * 40 + "\n")
                    f.write(f"Error: {result.get('error', 'Unknown error')}\n")
            
            return output_file
            
        except Exception as e:
            print(f"Failed to save result to file: {e}")
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
    # 中文测试案例
    jd_content_cn = """我们正在招聘一名高级产品经理，负责腾讯会议产品的规划和优化。
    
    职责包括：
    - 负责产品功能规划，与技术团队协作推进产品迭代
    - 分析用户需求和市场趋势，制定产品策略
    - 协调跨部门资源，推动产品目标达成
    - 监控产品数据，持续优化用户体验
    
    要求：
    - 3-5年产品经理经验，有B端或SaaS产品经验优先
    - 熟悉敏捷开发流程，有技术背景者优先
    - 优秀的数据分析和逻辑思维能力
    - 良好的沟通协调能力和项目管理能力
    """
    company_name_cn = "腾讯"
    position_title_cn = "高级产品经理-腾讯会议产品"
    
    # 英文测试案例
    jd_content_en = """We are seeking a Senior Software Engineer to join our engineering team at ByteDance.
    
    Responsibilities:
    - Design and develop scalable backend systems for our social media platform
    - Collaborate with cross-functional teams to deliver high-quality software solutions
    - Optimize system performance and ensure high availability
    - Mentor junior developers and contribute to technical documentation
    
    Requirements:
    - 5+ years of experience in backend development
    - Strong proficiency in Java, Python, or Go
    - Experience with distributed systems and microservices architecture
    - Excellent problem-solving skills and attention to detail
    """
    company_name_en = "ByteDance"
    position_title_en = "Senior Software Engineer"
    
    # 创建分析器实例 - 使用Gemini 2.5
    analyzer = JobAnalyzer(
        model="gemini-2.5-flash-lite",
        provider="gemini",
        temperature=0.3,
        max_tokens=10000
    )
    
    # 测试中文案例
    print("=" * 80)
    print("🇨🇳 中文测试案例")
    print("=" * 80)
    print(f"🏢 Company: {company_name_cn}")
    print(f"📋 Position: {position_title_cn}")
    print("🔄 Analyzing job position...")
    
    result_cn = analyzer.analyze_job(jd_content_cn, company_name_cn, position_title_cn, output_language="chinese")
    
    if result_cn["success"]:
        print("✅ Analysis successful!")
        print(result_cn["result"]["analysis"])
    else:
        print("❌ Analysis failed!")
        print(f"Error: {result_cn['error']}")
    
    print("\n" + "=" * 80)
    print("🇺🇸 English Test Case")
    print("=" * 80)
    print(f"🏢 Company: {company_name_en}")
    print(f"📋 Position: {position_title_en}")
    print("🔄 Analyzing job position...")
    
    # 测试英文案例
    analyzer = JobAnalyzer(
        model="gemini-2.5-flash-lite",
        provider="gemini",
        temperature=0.3,
        max_tokens=10000
    )
    
    result_en = analyzer.analyze_job(jd_content_en, company_name_en, position_title_en, output_language="english")
    
    if result_en["success"]:
        print("✅ Analysis successful!")
        print(result_en["result"]["analysis"])
    else:
        print("❌ Analysis failed!")
        print(f"Error: {result_en['error']}")
    
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    print(f"中文测试: {'✅' if result_cn['success'] else '❌'}")
    print(f"英文测试: {'✅' if result_en['success'] else '❌'}")