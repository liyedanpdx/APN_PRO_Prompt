#!/usr/bin/env python3
"""
Groq模型测试示例
演示如何快速切换不同的Groq模型进行测试
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test.candidate_tagger_test import CandidateTaggerPerformanceTest

# Groq可用模型列表
GROQ_MODELS = {
    "llama-3.1-70b-versatile": "Llama 3.1 70B - 最强推理能力",
    "llama-3.1-8b-instant": "Llama 3.1 8B - 快速响应",
    "llama-3.2-1b-preview": "Llama 3.2 1B - 轻量级模型", 
    "llama-3.2-3b-preview": "Llama 3.2 3B - 平衡性能",
    "mixtral-8x7b-32768": "Mixtral 8x7B - 长上下文",
    "gemma-7b-it": "Gemma 7B - Google模型",
    "gemma2-9b-it": "Gemma2 9B - 改进版本"
}

def quick_test_single_model(model_name: str, samples: int = 10):
    """快速测试单个模型"""
    print(f"\n{'='*50}")
    print(f"🧪 快速测试: {model_name}")
    print(f"📝 描述: {GROQ_MODELS.get(model_name, '未知模型')}")
    print(f"{'='*50}")
    
    test_runner = CandidateTaggerPerformanceTest()
    
    results = test_runner.concurrent_test(
        total_samples=samples,
        concurrent_limit=5,  # 较小的并发数用于快速测试
        model=model_name,
        provider="groq",
        temperature=0.0
    )
    
    # 简化输出
    perf = results["performance_metrics"]
    tokens = results["token_usage"]
    
    print(f"\n📊 快速结果:")
    print(f"  成功率: {perf['success_rate']:.1f}%")
    print(f"  平均响应时间: {perf['average_duration']:.3f}秒")
    print(f"  QPS: {perf['successful_requests_per_second']:.2f}")
    print(f"  平均Token: {tokens['average_total_tokens']:.1f}")
    
    return results

def compare_groq_models():
    """比较多个Groq模型的性能"""
    print("🚀 Groq模型性能对比测试")
    print("=" * 60)
    
    # 选择几个代表性模型进行对比
    test_models = [
        "llama-3.1-70b-versatile",  # 最强性能
        "llama-3.1-8b-instant",    # 快速响应
        "mixtral-8x7b-32768"       # 长上下文
    ]
    
    results_summary = []
    
    for model in test_models:
        result = quick_test_single_model(model, samples=20)
        
        perf = result["performance_metrics"]
        tokens = result["token_usage"]
        
        results_summary.append({
            "model": model,
            "success_rate": perf['success_rate'],
            "avg_duration": perf['average_duration'],
            "qps": perf['successful_requests_per_second'],
            "avg_tokens": tokens['average_total_tokens']
        })
    
    # 输出对比结果
    print(f"\n{'='*80}")
    print("📈 模型对比总结")
    print(f"{'='*80}")
    print(f"{'模型':<30} {'成功率':<8} {'平均时间':<10} {'QPS':<8} {'平均Token':<10}")
    print("-" * 80)
    
    for r in results_summary:
        print(f"{r['model']:<30} {r['success_rate']:<7.1f}% {r['avg_duration']:<9.3f}s {r['qps']:<7.2f} {r['avg_tokens']:<9.1f}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 单模型测试
        model_name = sys.argv[1]
        if model_name in GROQ_MODELS:
            samples = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            quick_test_single_model(model_name, samples)
        else:
            print(f"❌ 未知模型: {model_name}")
            print("可用模型:")
            for model, desc in GROQ_MODELS.items():
                print(f"  {model} - {desc}")
    else:
        # 模型对比测试
        compare_groq_models()