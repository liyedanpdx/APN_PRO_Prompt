#!/usr/bin/env python3
"""
快速测试CandidateTagger中的LLMClient问题
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.llm import LLMClient
from function.candidate_tagger import CandidateTagger

def test_direct_llm_client():
    """直接测试LLM客户端"""
    print("🧪 直接测试LLM客户端...")
    
    llm = LLMClient()
    
    test_messages = [{"role": "user", "content": "Say hello"}]
    
    # 测试Gemini
    response = llm.call_llm(
        provider="gemini",
        model="gemini-2.5-flash-lite", 
        messages=test_messages,
        temperature=0.1,
        max_tokens=10
    )
    
    print(f"直接调用结果: success={response.get('success')}")
    if response.get('success'):
        print(f"响应: {llm.get_response_content(response)}")
    else:
        print(f"错误: {response.get('error')}")

def test_candidate_tagger_llm():
    """测试CandidateTagger中的LLM客户端"""
    print("\n🧪 测试CandidateTagger中的LLM客户端...")
    
    tagger = CandidateTagger(
        model="gemini-2.5-flash-lite",
        provider="gemini",
        temperature=0.1,
        max_tokens=10
    )
    
    test_messages = [{"role": "user", "content": "Say hello"}]
    
    # 直接测试tagger内部的LLM客户端
    response = tagger.llm_client.call_llm(
        provider="gemini",
        model="gemini-2.5-flash-lite",
        messages=test_messages,
        temperature=0.1,
        max_tokens=10
    )
    
    print(f"Tagger内部调用结果: success={response.get('success')}")
    if response.get('success'):
        print(f"响应: {tagger.llm_client.get_response_content(response)}")
    else:
        print(f"错误: {response.get('error')}")

def test_candidate_tagger_full():
    """测试CandidateTagger完整流程"""
    print("\n🧪 测试CandidateTagger完整流程...")
    
    tagger = CandidateTagger(
        model="gemini-2.5-flash-lite",
        provider="gemini",
        temperature=0.1,
        max_tokens=500
    )
    
    # 测试实际的候选人标签功能
    test_text = "We are looking for a backend engineer for our financial department. We hope this candidate have more than 5 years"
    
    result = tagger.analyze_text(test_text)
    
    print(f"完整流程结果: success={result.get('success')}")
    if result.get('success'):
        print(f"解析结果: {result.get('result')}")
        print(f"原始响应长度: {len(result.get('raw_content', ''))}")
    else:
        print(f"错误: {result.get('error')}")
        if 'raw_content' in result:
            print(f"原始内容: {result['raw_content']}")

def test_with_debug_params():
    """测试参数传递"""
    print("\n🧪 测试参数传递...")
    
    tagger = CandidateTagger(
        model="gemini-2.5-flash-lite", 
        provider="gemini",
        temperature=0.1,
        max_tokens=500,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    
    print(f"Tagger参数:")
    print(f"  temperature: {tagger.temperature}")
    print(f"  frequency_penalty: {tagger.frequency_penalty}")
    print(f"  presence_penalty: {tagger.presence_penalty}")
    
    # 测试简单调用
    test_text = "Backend engineer needed"
    result = tagger.analyze_text(test_text)
    
    print(f"参数测试结果: success={result.get('success')}")
    if not result.get('success'):
        print(f"错误: {result.get('error')}")

if __name__ == "__main__":
    print("🔍 开始诊断CandidateTagger和LLMClient的集成问题...")
    print("=" * 60)
    
    test_direct_llm_client()
    test_candidate_tagger_llm() 
    test_candidate_tagger_full()
    test_with_debug_params()
    
    print("\n🎯 诊断完成！")