#!/usr/bin/env python3
"""
示例：如何使用CandidateTagger进行候选人标签分析
"""

import json
from function.candidate_tagger import CandidateTagger


def main():
    # 创建候选人标签器实例 - 使用GPT-4.1 nano
    tagger = CandidateTagger(
        model="gpt-4.1-nano-2025-04-14", 
        provider="openai",
        temperature=0.1,     # 低温度确保一致性
        max_tokens=500,      # 限制输出长度
        top_p=0.9,          # 核采样参数
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    
    # 测试文本
    test_queries = [
        "We are looking for a backend engineer for our financial department. We hope this candidate have more than 5 years",
        "Looking for Python developers in New York with machine learning experience",
        "Senior frontend developer needed for startup in San Francisco",
        "Data scientist with PhD in statistics for pharmaceutical company",
        "Remote DevOps engineer with AWS certification and 3+ years experience"
    ]
    
    print("=== 候选人标签分析示例 ===\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"测试查询 {i}:")
        print(f"输入: {query}")
        print("-" * 50)
        
        # 分析文本
        result = tagger.analyze_text(query)
        
        if result["success"]:
            # 格式化输出结果
            analysis_result = result["result"]
            print("分析结果:")
            print(json.dumps(analysis_result, indent=2, ensure_ascii=False))
            
            # 显示使用的token数
            if "usage" in result:
                usage = result["usage"]
                print(f"\n使用的Tokens: {usage.get('total_tokens', 'N/A')}")
                print(f"模型: {result.get('model_used', 'N/A')}")
        
        else:
            print(f"分析失败: {result['error']}")
        
        print("\n" + "="*60 + "\n")
    
    # 批量分析示例
    print("=== 批量分析示例 ===")
    batch_results = tagger.batch_analyze(test_queries)
    
    # 获取统计信息
    stats = tagger.get_summary_stats(batch_results)
    print(f"批量分析统计:")
    print(f"总数: {stats['total_analyzed']}")
    print(f"成功: {stats['successful']}")
    print(f"失败: {stats['failed']}")
    print(f"成功率: {stats['success_rate']:.1%}")
    
    print("\n维度出现频率:")
    for dimension, percentage in stats['dimension_percentages'].items():
        print(f"  {dimension}: {percentage:.1f}%")


if __name__ == "__main__":
    main()