#!/usr/bin/env python3
"""
Gemini响应调试工具
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from function.candidate_tagger import CandidateTagger

def debug_gemini_response():
    """调试Gemini的具体响应内容"""
    print("🔍 调试Gemini响应...")
    print("=" * 50)
    
    # 创建标签器实例
    tagger = CandidateTagger(
        model="gemini-2.5-flash-lite",
        provider="gemini",
        temperature=0.0,
        max_tokens=500
    )
    
    # 测试文本
    test_text = "We are looking for a backend engineer for our financial department. We hope this candidate have more than 5 years"
    
    print(f"📝 测试文本: {test_text}")
    print("-" * 50)
    
    # 分析文本
    result = tagger.analyze_text(test_text)
    
    print("🔍 完整响应结构:")
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
    print(f"Provider: {result.get('provider')}")
    print(f"Model: {result.get('model_used')}")
    
    if 'raw_content' in result:
        print(f"\n📋 原始响应内容:")
        print(f"类型: {type(result['raw_content'])}")
        print(f"长度: {len(result['raw_content']) if result['raw_content'] else 0}")
        print(f"内容: '{result['raw_content']}'")
        
        # 尝试手动解析
        print(f"\n🔧 手动解析测试:")
        try:
            import json
            content = result['raw_content'].strip()
            
            # 检查是否有markdown标记
            if content.startswith("```json"):
                print("✅ 发现markdown json标记")
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                print("✅ 发现markdown标记")
                content = content.replace("```", "").strip()
            
            print(f"清理后内容: '{content}'")
            
            # 尝试解析JSON
            parsed = json.loads(content)
            print("✅ JSON解析成功!")
            print(f"解析结果: {parsed}")
            
            # 验证格式
            if "result" in parsed:
                print("✅ 包含result字段")
                if isinstance(parsed["result"], list) and len(parsed["result"]) == 5:
                    print("✅ result是5元素列表")
                    for i, item in enumerate(parsed["result"]):
                        if "label" in item and "containsCriteria" in item:
                            print(f"✅ 项目{i+1}: {item['label']} = {item['containsCriteria']}")
                        else:
                            print(f"❌ 项目{i+1}格式错误: {item}")
                else:
                    print(f"❌ result格式错误: {type(parsed['result'])}, 长度: {len(parsed['result']) if isinstance(parsed['result'], list) else 'N/A'}")
            else:
                print("❌ 缺少result字段")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"尝试查找JSON内容...")
            
            # 尝试从响应中提取JSON部分
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    print(f"发现可能的JSON起始行 {i}: '{line}'")
                if line.strip().endswith('}'):
                    print(f"发现可能的JSON结束行 {i}: '{line}'")
                    
        except Exception as e:
            print(f"❌ 其他解析错误: {e}")
    
    if 'result' in result:
        print(f"\n✅ 最终解析结果: {result['result']}")
    
    if 'usage' in result:
        print(f"\n🪙 Token使用: {result['usage']}")

if __name__ == "__main__":
    debug_gemini_response()