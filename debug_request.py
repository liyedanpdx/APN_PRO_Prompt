#!/usr/bin/env python3
"""
详细调试Gemini API请求
"""

import sys
import json
import requests
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config

def debug_gemini_request():
    """详细调试Gemini API请求"""
    print("🔍 详细调试Gemini API请求...")
    print("=" * 50)
    
    config = Config()
    
    print(f"📋 配置信息：")
    print(f"  API Key: {config.GEMINI_API_KEY[:10]}...{config.GEMINI_API_KEY[-4:]}")
    print(f"  API Base: {config.GEMINI_API_BASE}")
    print(f"  默认模型: {config.GEMINI_DEFAULT_MODEL}")
    
    # 构建请求
    url = f"{config.GEMINI_API_BASE}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {config.GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 简化的payload - 只包含基本参数
    simple_payload = {
        "model": "gemini-2.5-flash-lite",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.1,
        "max_tokens": 10
    }
    
    print(f"\n📤 请求信息：")
    print(f"  URL: {url}")
    print(f"  Headers: {headers}")
    print(f"  Payload: {json.dumps(simple_payload, indent=2)}")
    
    # 发送请求
    print(f"\n🚀 发送请求...")
    try:
        response = requests.post(url, json=simple_payload, headers=headers)
        print(f"  状态码: {response.status_code}")
        print(f"  响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 请求成功!")
            data = response.json()
            print(f"  响应: {json.dumps(data, indent=2)}")
        else:
            print("❌ 请求失败!")
            print(f"  错误信息: {response.text}")
            
            # 尝试不同的payload格式
            print(f"\n🔄 尝试不同的payload格式...")
            
            # 1. 移除max_tokens
            payload2 = {
                "model": "gemini-2.5-flash-lite",
                "messages": [{"role": "user", "content": "Hello"}],
                "temperature": 0.1
            }
            
            print(f"尝试移除max_tokens...")
            response2 = requests.post(url, json=payload2, headers=headers)
            print(f"  状态码: {response2.status_code}")
            if response2.status_code != 200:
                print(f"  错误: {response2.text}")
            else:
                print("✅ 成功!")
                
            # 2. 尝试不同的模型名
            payload3 = {
                "model": "gemini-1.5-flash",
                "messages": [{"role": "user", "content": "Hello"}]
            }
            
            print(f"尝试不同模型名...")
            response3 = requests.post(url, json=payload3, headers=headers)
            print(f"  状态码: {response3.status_code}")
            if response3.status_code != 200:
                print(f"  错误: {response3.text}")
            else:
                print("✅ 成功!")
                
            # 3. 尝试不同的URL
            alt_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
            print(f"尝试原生API URL: {alt_url}")
            
            native_payload = {
                "contents": [{"parts": [{"text": "Hello"}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 10
                }
            }
            
            native_headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": config.GEMINI_API_KEY
            }
            
            response4 = requests.post(alt_url, json=native_payload, headers=native_headers)
            print(f"  状态码: {response4.status_code}")
            if response4.status_code != 200:
                print(f"  错误: {response4.text}")
            else:
                print("✅ 原生API成功!")
                print(f"  响应: {response4.json()}")
    
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    debug_gemini_request()