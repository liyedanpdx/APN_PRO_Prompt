import openai
import requests
import json
from typing import Dict, Any, Optional, List, Generator, Callable
import sys
from pathlib import Path
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import Config

class LLMClient:
    def __init__(self):
        self.config = Config()
        
    def call_openai(
        self,
        model: str = "gpt-4-1106-preview",
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一调用OpenAI API
        
        Args:
            model: 模型名称，如 "gpt-4-1106-preview", "gpt-3.5-turbo" 等
            messages: 消息列表 [{"role": "user", "content": "text"}]
            temperature: 温度参数 (0-2)
            max_tokens: 最大token数
            top_p: 核采样参数 (0-1)
            frequency_penalty: 频率惩罚 (-2.0 to 2.0)
            presence_penalty: 存在惩罚 (-2.0 to 2.0)
            stop: 停止序列
            **kwargs: 其他参数
        
        Returns:
            API响应字典
        """
        client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages or [],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                **kwargs
            )
            
            return {
                "success": True,
                "data": {
                    "choices": [
                        {
                            "message": {
                                "role": choice.message.role,
                                "content": choice.message.content
                            },
                            "finish_reason": choice.finish_reason
                        } for choice in response.choices
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "model": response.model
                },
                "provider": "openai"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }
    
    def call_perplexity(
        self,
        model: str = "llama-3.1-sonar-small-128k-online",
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        top_p: float = 0.9,
        top_k: int = 0,
        stream: bool = False,
        presence_penalty: float = 0,
        frequency_penalty: float = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一调用Perplexity API - 使用 OpenAI 客户端库
        
        Args:
            model: 模型名称，如 "sonar-pro", "llama-3.1-sonar-small-128k-online" 等
            messages: 消息列表 [{"role": "user", "content": "text"}]
            temperature: 温度参数 (0-2)
            max_tokens: 最大token数
            top_p: 核采样参数 (0-1)
            top_k: top-k采样参数
            stream: 是否流式输出
            presence_penalty: 存在惩罚
            frequency_penalty: 频率惩罚
            **kwargs: 其他参数
        
        Returns:
            API响应字典
        """
        # 使用 OpenAI 客户端库，但指向 Perplexity 的端点
        client = openai.OpenAI(
            api_key=self.config.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages or [],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=stream,
                **kwargs
            )
            
            return {
                "success": True,
                "data": {
                    "choices": [
                        {
                            "message": {
                                "role": response.choices[0].message.role,
                                "content": response.choices[0].message.content
                            },
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "model": response.model
                },
                "provider": "perplexity"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "perplexity"
            }
    
    def call_groq(
        self,
        model: str = "llama-3.1-70b-versatile",
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        stream: bool = False,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一调用Groq API
        
        Args:
            model: 模型名称，如 "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768" 等
            messages: 消息列表 [{"role": "user", "content": "text"}]
            temperature: 温度参数 (0-2)
            max_tokens: 最大token数
            top_p: 核采样参数 (0-1)
            stream: 是否流式输出
            stop: 停止序列
            **kwargs: 其他参数
        
        Returns:
            API响应字典
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages or [],
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "data": data,
                "provider": "groq"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "groq"
            }
    
    def call_ali(
        self,
        model: str = "deepseek-v3",
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        stream: bool = False,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一调用阿里云API (通过DashScope兼容OpenAI格式)
        
        Args:
            model: 模型名称，如 "deepseek-v3", "qwen-max", "qwen-turbo" 等
            messages: 消息列表 [{"role": "user", "content": "text"}]
            temperature: 温度参数 (0-2)
            max_tokens: 最大token数
            top_p: 核采样参数 (0-1)
            stream: 是否流式输出
            stop: 停止序列
            **kwargs: 其他参数
        
        Returns:
            API响应字典
        """
        url = f"{self.config.ALI_API_BASE}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.ALI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages or [],
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "data": data,
                "provider": "ali"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "ali"
            }
    
    def call_gemini(
        self,
        model: str = "gemini-2.5-flash-lite",
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        stream: bool = False,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一调用Gemini API (通过OpenAI兼容格式)
        
        Args:
            model: 模型名称，如 "gemini-2.5-flash-lite", "gemini-1.5-pro" 等
            messages: 消息列表 [{"role": "user", "content": "text"}]
            temperature: 温度参数 (0-2)
            max_tokens: 最大token数
            top_p: 核采样参数 (0-1)
            stream: 是否流式输出
            stop: 停止序列
            **kwargs: 其他参数
        
        Returns:
            API响应字典
        """
        url = f"{self.config.GEMINI_API_BASE}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.GEMINI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Gemini支持的参数（过滤掉不支持的参数）
        supported_params = {}
        for key, value in kwargs.items():
            if key not in ['frequency_penalty', 'presence_penalty']:
                supported_params[key] = value
        
        payload = {
            "model": model,
            "messages": messages or [],
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            **supported_params
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "data": data,
                "provider": "gemini"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "gemini"
            }
    
    def call_llm(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一LLM调用接口
        
        Args:
            provider: 提供商 ("openai", "perplexity", "groq", "ali", "gemini")
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数
        
        Returns:
            API响应字典
        """
        if provider.lower() == "openai":
            return self.call_openai(model=model, messages=messages, **kwargs)
        elif provider.lower() == "perplexity":
            return self.call_perplexity(model=model, messages=messages, **kwargs)
        elif provider.lower() == "groq":
            return self.call_groq(model=model, messages=messages, **kwargs)
        elif provider.lower() == "ali":
            return self.call_ali(model=model, messages=messages, **kwargs)
        elif provider.lower() == "gemini":
            return self.call_gemini(model=model, messages=messages, **kwargs)
        else:
            return {
                "success": False,
                "error": f"Unsupported provider: {provider}",
                "provider": provider
            }
    
    def get_response_content(self, response: Dict[str, Any]) -> Optional[str]:
        """
        从响应中提取内容文本
        
        Args:
            response: LLM API响应
            
        Returns:
            响应内容文本
        """
        if not response.get("success"):
            return None
            
        data = response.get("data", {})
        
        if response.get("provider") == "openai":
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
        elif response.get("provider") == "perplexity":
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
        elif response.get("provider") == "groq":
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
        elif response.get("provider") == "ali":
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
        elif response.get("provider") == "gemini":
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content")
        
        return None
    
    def stream_llm(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        """
        流式调用LLM接口 - 简单直接返回流对象
        
        Args:
            provider: 提供商 ("openai", "gemini", "ali", "groq")
            model: 模型名称
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            流对象，可以直接迭代使用
        """
        kwargs['stream'] = True
        
        if provider.lower() == "openai":
            return self._stream_openai(model, messages, **kwargs)
        elif provider.lower() == "gemini":
            return self._stream_gemini(model, messages, **kwargs)
        elif provider.lower() == "ali":
            return self._stream_ali(model, messages, **kwargs)
        elif provider.lower() == "groq":
            return self._stream_groq(model, messages, **kwargs)
        elif provider.lower() == "perplexity":
            return self._stream_perplexity(model, messages, **kwargs)
        else:
            raise ValueError(f"Unsupported provider for streaming: {provider}")
    
    def _stream_openai(self, model: str, messages: List[Dict[str, str]], **kwargs):
        """OpenAI 流式生成 - 使用原生 OpenAI API"""
        client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
        return client.chat.completions.create(
            model=model,
            messages=messages or [],
            **kwargs
        )
    
    def _stream_gemini(self, model: str, messages: List[Dict[str, str]], **kwargs):
        """Gemini 流式生成 - 使用 OpenAI 客户端库统一接口"""
        # 使用 OpenAI 客户端库，但指向 Gemini 的端点
        client = openai.OpenAI(
            api_key=self.config.GEMINI_API_KEY,
            base_url=self.config.GEMINI_API_BASE
        )
        
        # 过滤掉不支持的参数
        supported_params = {}
        for key, value in kwargs.items():
            if key not in ['frequency_penalty', 'presence_penalty']:
                supported_params[key] = value
        
        return client.chat.completions.create(
            model=model,
            messages=messages or [],
            **supported_params
        )
    
    def _stream_ali(self, model: str, messages: List[Dict[str, str]], **kwargs):
        """阿里云 流式生成 - 返回requests流对象"""
        url = f"{self.config.ALI_API_BASE}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.ALI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages or [],
            **kwargs
        }
        
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()
        return response
    
    def _stream_groq(self, model: str, messages: List[Dict[str, str]], **kwargs):
        """Groq 流式生成 - 返回requests流对象"""
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages or [],
            **kwargs
        }
        
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()
        return response
    
    def _stream_perplexity(self, model: str, messages: List[Dict[str, str]], **kwargs):
        """Perplexity 流式生成 - 使用 OpenAI 客户端库统一接口"""
        # 使用 OpenAI 客户端库，但指向 Perplexity 的端点
        client = openai.OpenAI(
            api_key=self.config.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        
        return client.chat.completions.create(
            model=model,
            messages=messages or [],
            **kwargs
        )


# 预设模型配置
OPENAI_MODELS = {
    "gpt-4-turbo": "gpt-4-1106-preview",
    "gpt-4": "gpt-4",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k": "gpt-3.5-turbo-16k"
}

PERPLEXITY_MODELS = {
    "sonar-small": "llama-3.1-sonar-small-128k-online",
    "sonar-large": "llama-3.1-sonar-large-128k-online",
    "sonar-huge": "llama-3.1-sonar-huge-128k-online"
}

GROQ_MODELS = {
    "llama-3.1-70b": "llama-3.1-70b-versatile",
    "llama-3.1-8b": "llama-3.1-8b-instant",
    "llama-3.2-1b": "llama-3.2-1b-preview",
    "llama-3.2-3b": "llama-3.2-3b-preview",
    "mixtral-8x7b": "mixtral-8x7b-32768",
    "gemma-7b": "gemma-7b-it",
    "gemma2-9b": "gemma2-9b-it"
}

ALI_MODELS = {
    "deepseek-v3": "deepseek-v3",
    "qwen-max": "qwen-max",
    "qwen-turbo": "qwen-turbo", 
    "qwen-plus": "qwen-plus",
    "qwen-long": "qwen-long",
    "qwen2.5-72b": "qwen2.5-72b-instruct",
    "qwen2.5-32b": "qwen2.5-32b-instruct",
    "qwen2.5-14b": "qwen2.5-14b-instruct",
    "qwen2.5-7b": "qwen2.5-7b-instruct"
}

GEMINI_MODELS = {
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    "gemini-1.5-pro": "gemini-1.5-pro",
    "gemini-1.5-flash": "gemini-1.5-flash",
    "gemini-1.0-pro": "gemini-1.0-pro"
}

# 使用示例和测试
if __name__ == "__main__":
    print("🚀 开始测试所有LLM提供商...")
    print("=" * 60)
    
    llm = LLMClient()
    
    # 测试消息
    test_messages = [
        {"role": "user", "content": "who are you?"}
    ]
    
    # 1. OpenAI测试
    print("\n1️⃣ 测试 OpenAI...")
    try:
        openai_response = llm.call_openai(
            model="gpt-4-1106-preview",
            messages=test_messages,
            temperature=0.1,
            max_tokens=10
        )
        
        if openai_response["success"]:
            print("✅ OpenAI 调用成功")
            print(f"📝 响应: {llm.get_response_content(openai_response)}")
            if "usage" in openai_response.get("data", {}):
                usage = openai_response["data"]["usage"]
                print(f"🪙 Token使用: {usage}")
        else:
            print(f"❌ OpenAI 调用失败: {openai_response['error']}")
    except Exception as e:
        print(f"❌ OpenAI 异常: {e}")
    
    # 2. Perplexity测试  
    print("\n2️⃣ 测试 Perplexity...")
    try:
        perplexity_response = llm.call_perplexity(
            model="sonar",
            messages=test_messages,
            temperature=0.1,
            max_tokens=10
        )
        
        if perplexity_response["success"]:
            print("✅ Perplexity 调用成功")
            print(f"📝 响应: {llm.get_response_content(perplexity_response)}")
            if "usage" in perplexity_response.get("data", {}):
                usage = perplexity_response["data"]["usage"]
                print(f"🪙 Token使用: {usage}")
        else:
            print(f"❌ Perplexity 调用失败: {perplexity_response['error']}")
    except Exception as e:
        print(f"❌ Perplexity 异常: {e}")
    
    # 3. Groq测试
    print("\n3️⃣ 测试 Groq...")
    try:
        groq_response = llm.call_groq(
            model="llama-3.1-70b-versatile",
            messages=test_messages,
            temperature=0.1,
            max_tokens=10
        )
        
        if groq_response["success"]:
            print("✅ Groq 调用成功")
            print(f"📝 响应: {llm.get_response_content(groq_response)}")
            if "usage" in groq_response.get("data", {}):
                usage = groq_response["data"]["usage"]
                print(f"🪙 Token使用: {usage}")
        else:
            print(f"❌ Groq 调用失败: {groq_response['error']}")
    except Exception as e:
        print(f"❌ Groq 异常: {e}")
    
    # 4. Ali (阿里云) 测试
    print("\n4️⃣ 测试 Ali (阿里云)...")
    try:
        ali_response = llm.call_ali(
            model="deepseek-v3",
            messages=test_messages,
            temperature=0.1,
            max_tokens=10
        )
        
        if ali_response["success"]:
            print("✅ Ali 调用成功")
            print(f"📝 响应: {llm.get_response_content(ali_response)}")
            if "usage" in ali_response.get("data", {}):
                usage = ali_response["data"]["usage"]
                print(f"🪙 Token使用: {usage}")
        else:
            print(f"❌ Ali 调用失败: {ali_response['error']}")
    except Exception as e:
        print(f"❌ Ali 异常: {e}")
    
    # 5. Gemini测试
    print("\n5️⃣ 测试 Gemini...")
    try:
        gemini_response = llm.call_gemini(
            model="gemini-2.5-flash-lite",
            messages=test_messages,
            temperature=0.1,
            max_tokens=10,
            stream=True
        )
        
        if gemini_response["success"]:
            print("✅ Gemini 调用成功")
            print(f"📝 响应: {llm.get_response_content(gemini_response)}")
            if "usage" in gemini_response.get("data", {}):
                usage = gemini_response["data"]["usage"]
                print(f"🪙 Token使用: {usage}")
        else:
            print(f"❌ Gemini 调用失败: {gemini_response['error']}")
    except Exception as e:
        print(f"❌ Gemini 异常: {e}")
    
    # 6. 统一接口测试
    print("\n6️⃣ 测试统一接口 call_llm()...")
    providers_to_test = [
        ("openai", "gpt-4-1106-preview"),
        ("perplexity", "llama-3.1-sonar-small-128k-online"), 
        ("groq", "llama-3.1-70b-versatile"),
        ("ali", "deepseek-v3"),
        ("gemini", "gemini-2.5-flash-lite")
    ]
    
    for provider, model in providers_to_test:
        try:
            print(f"\n🔄 测试统一接口: {provider} - {model}")
            response = llm.call_llm(
                provider=provider,
                model=model,
                messages=test_messages,
                temperature=0.1,
                max_tokens=10
            )
            
            if response["success"]:
                print(f"✅ {provider} 统一接口调用成功")
                content = llm.get_response_content(response)
                print(f"📝 响应: {content}")
            else:
                print(f"❌ {provider} 统一接口调用失败: {response['error']}")
        except Exception as e:
            print(f"❌ {provider} 统一接口异常: {e}")
    
    # 7. 流式生成测试
    print("\n7️⃣ 测试流式生成...")
    test_stream_providers = [
        ("openai", "gpt-4-1106-preview"),
        ("gemini", "gemini-2.5-flash-lite"),
        ("groq", "llama-3.1-70b-versatile"),
        ("ali", "deepseek-v3")
    ]
    
    stream_test_messages = [
        {"role": "user", "content": "请用50个字介绍一下人工智能的发展历史。"}
    ]
    
    # 测试 OpenAI 流式生成（参考 stream_api_test.py 的简单方式）
    print(f"\n🌊 测试流式生成: OpenAI")
    try:
        print(f"📝 流式响应: ", end="", flush=True)
        start_time = time.time()
        
        # 获取流对象
        stream = llm.stream_llm(
            provider="openai",
            model="gpt-4-1106-preview",
            messages=stream_test_messages,
            temperature=0.3,
            max_tokens=100
        )
        
        # 像 stream_api_test.py 一样简单处理流
        chunk_count = 0
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end='', flush=True)
                chunk_count += 1
        
        end_time = time.time()
        print()  # 换行
        print(f"✅ OpenAI 流式生成成功")
        print(f"📊 统计: {chunk_count} 个块")
        print(f"⏱️ 耗时: {end_time - start_time:.2f}s")
        
    except Exception as e:
        print(f"❌ OpenAI 流式生成异常: {e}")
    
    # 测试 Gemini 流式生成（现在也使用 OpenAI 客户端库统一接口）
    print(f"\n🌊 测试流式生成: Gemini")
    try:
        print(f"📝 流式响应: ", end="", flush=True)
        start_time = time.time()
        
        # 获取流对象 - 现在 Gemini 也返回和 OpenAI 相同的流对象
        stream = llm.stream_llm(
            provider="gemini",
            model="gemini-2.5-flash-lite",
            messages=stream_test_messages,
            temperature=0.3,
            max_tokens=100
        )
        
        # 像 OpenAI 一样处理流
        chunk_count = 0
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end='', flush=True)
                chunk_count += 1
        
        end_time = time.time()
        print()  # 换行
        print(f"✅ Gemini 流式生成成功")
        print(f"📊 统计: {chunk_count} 个块")
        print(f"⏱️ 耗时: {end_time - start_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Gemini 流式生成异常: {e}")
    
    # 测试 Perplexity 流式生成（也使用 OpenAI 客户端库统一接口）
    print(f"\n🌊 测试流式生成: Perplexity")
    try:
        print(f"📝 流式响应: ", end="", flush=True)
        start_time = time.time()
        
        # 获取流对象 - 现在 Perplexity 也返回和 OpenAI 相同的流对象
        stream = llm.stream_llm(
            provider="perplexity",
            model="sonar-pro",#"sonar-reasoning",
            messages=[{"role": "user", "content": "Compare renewable energy technologies"}],
            temperature=0.3
        )
        
        # 像 OpenAI 一样处理流，但包含 Perplexity 的额外信息处理
        chunk_count = 0
        content = ""
        search_results = []
        usage_info = None
        
        for chunk in stream:
            # Content arrives progressively
            if chunk.choices[0].delta.content is not None:
                content_chunk = chunk.choices[0].delta.content
                content += content_chunk
                print(content_chunk, end="", flush=True)
                chunk_count += 1
            
            # Metadata arrives in final chunks (Perplexity specific)
            if hasattr(chunk, 'search_results') and chunk.search_results:
                search_results = chunk.search_results
            
            if hasattr(chunk, 'usage') and chunk.usage:
                usage_info = chunk.usage
            
            # Handle completion
            if chunk.choices[0].finish_reason is not None:
                print(f"\n\nFinish reason: {chunk.choices[0].finish_reason}")
                if search_results:
                    print(f"Search Results: {len(search_results)} results found")
                if usage_info:
                    print(f"Usage: {usage_info}")
        
        end_time = time.time()
        print(f"✅ Perplexity 流式生成成功")
        print(f"📊 统计: {chunk_count} 个块")
        print(f"⏱️ 耗时: {end_time - start_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Perplexity 流式生成异常: {e}")
    
    # 测试其他提供商的流式处理（仍使用 requests 流）
    other_providers = [("groq", "llama-3.1-70b-versatile")]
    
    for provider, model in other_providers:
        print(f"\n🌊 测试流式生成: {provider}")
        try:
            print(f"📝 流式响应: ", end="", flush=True)
            start_time = time.time()
            
            # 获取流对象
            response = llm.stream_llm(
                provider=provider,
                model=model,
                messages=stream_test_messages,
                temperature=0.3,
                max_tokens=100
            )
            
            # 处理 requests 流
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and data['choices']:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                                    chunk_count += 1
                        except json.JSONDecodeError:
                            continue
            
            end_time = time.time()
            print()  # 换行
            print(f"✅ {provider} 流式生成成功")
            print(f"📊 统计: {chunk_count} 个块")
            print(f"⏱️ 耗时: {end_time - start_time:.2f}s")
            
        except Exception as e:
            print(f"❌ {provider} 流式生成异常: {e}")
    
    print(f"\n{'=' * 60}")
    print("🎯 测试完成！请检查上述结果以确认各提供商的工作状态。")
    print("🌊 流式生成功能已添加，支持实时接收和处理文本流。")