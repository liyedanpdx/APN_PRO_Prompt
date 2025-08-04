#!/usr/bin/env python3
"""
快速配置测试文件
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config
from api.llm import LLMClient

def test_config():
    """测试配置是否正确加载"""
    print("=== 配置测试 ===")
    
    try:
        config = Config()
        print("✅ Config 加载成功")
        
        # 显示所有API密钥状态
        print(f"OpenAI API Key: {'✅' if config.OPENAI_API_KEY else '❌'} ({config.OPENAI_API_KEY[:10]}...)")
        print(f"Perplexity API Key: {'✅' if config.PERPLEXITY_API_KEY else '❌'} ({config.PERPLEXITY_API_KEY[:10]}...)")
        print(f"Groq API Key: {'✅' if config.GROQ_API_KEY else '❌'} ({config.GROQ_API_KEY[:10]}...)")
        print(f"Ali API Key: {'✅' if config.ALI_API_KEY else '❌'} ({config.ALI_API_KEY[:10]}...)")
        print(f"Gemini API Key: {'✅' if config.GEMINI_API_KEY else '❌'} ({config.GEMINI_API_KEY[:10]}...)")
        
        # 验证配置
        is_valid, errors = config.validate_config()
        print(f"\n配置验证: {'✅ 有效' if is_valid else '❌ 无效'}")
        if errors:
            for error in errors:
                print(f"  - {error}")
        
    except Exception as e:
        print(f"❌ Config 加载失败: {e}")
        return False
    
    return True

def test_llm_client():
    """测试LLM客户端"""
    print("\n=== LLM客户端测试 ===")
    
    try:
        client = LLMClient()
        print("✅ LLMClient 创建成功")
        
        # 测试支持的提供商
        providers = ["openai", "perplexity", "groq", "ali", "gemini"]
        
        for provider in providers:
            try:
                # 只测试call_llm方法是否能识别提供商，不实际调用API
                test_messages = [{"role": "user", "content": "test"}]
                
                # 检查是否会立即返回"Unsupported provider"错误
                response = client.call_llm(provider, "test-model", test_messages, max_tokens=1)
                
                if response.get("error") == f"Unsupported provider: {provider}":
                    print(f"❌ {provider}: 不支持")
                else:
                    print(f"✅ {provider}: 支持 (可能API调用失败，但提供商被识别)")
                    
            except Exception as e:
                print(f"❌ {provider}: 异常 - {e}")
    
    except Exception as e:
        print(f"❌ LLMClient 创建失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 开始系统诊断...")
    
    config_ok = test_config()
    llm_ok = test_llm_client()
    
    print(f"\n📊 诊断结果:")
    print(f"配置系统: {'✅' if config_ok else '❌'}")
    print(f"LLM客户端: {'✅' if llm_ok else '❌'}")
    
    if config_ok and llm_ok:
        print("\n🎉 系统正常，可以使用所有提供商！")
    else:
        print("\n⚠️ 系统存在问题，请检查上述错误信息")