#!/usr/bin/env python3
"""
候选人标签器性能测试工具
支持并发测试、自定义参数、详细统计分析
"""

import sys
import time
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from function.candidate_tagger import CandidateTagger


class CandidateTaggerPerformanceTest:
    """候选人标签器性能测试类"""
    
    def __init__(self):
        self.test_samples = self._generate_test_samples()
        
    def _generate_test_samples(self) -> List[str]:
        """生成测试样本数据"""
        return [
            "We are looking for a backend engineer for our financial department with more than 5 years experience",
            "Senior Python developer needed in New York with machine learning expertise",
            "Remote DevOps engineer with AWS certification and 3+ years experience required",
            "Data scientist with PhD in statistics for pharmaceutical company in Boston",
            "Frontend developer for startup in San Francisco, React experience preferred",
            "Looking for Java developers with Spring Boot experience in London",
            "Senior AI engineer needed for tech company with computer vision skills",
            "Product manager with 7+ years experience in fintech industry",
            "Full-stack developer position available in Berlin, remote work possible",
            "Cybersecurity analyst needed with CISSP certification and 5 years experience",
            "UX designer for e-commerce platform in Seattle, portfolio required",
            "Database administrator with Oracle expertise for healthcare company",
            "Cloud architect position in Singapore with Azure and GCP experience",
            "Mobile app developer needed with Flutter and React Native skills",
            "Business analyst for consulting firm in Chicago with SQL knowledge",
            "Network engineer with Cisco certification for telecom company",
            "QA engineer position available with automation testing experience",
            "Technical writer needed for software company with API documentation skills",
            "Solutions architect role in Toronto with microservices experience",
            "Site reliability engineer needed with Kubernetes and Docker expertise",
            "Marketing manager position in Austin with digital marketing background",
            "HR specialist needed for startup with talent acquisition experience",
            "Financial analyst role available with CPA certification preferred",
            "Operations manager needed in Denver with supply chain experience",
            "Legal counsel position for technology company with IP law background",
            "Sales engineer needed with technical background in software industry",
            "Research scientist position available with machine learning PhD",
            "Project manager role in Miami with PMP certification required",
            "Customer success manager needed with SaaS platform experience",
            "Strategy consultant position available with MBA from top university",
            "Backend engineer for fintech startup",
            "Senior developer needed",
            "Looking for Python programmers",
            "Remote work opportunity",
            "5+ years experience required",
            "New York based position",
            "Startup environment",
            "Machine learning skills",
            "Full-time position",
            "Competitive salary offered",
            "Healthcare company seeking data analyst with 3 years experience in Chicago",
            "Seeking experienced software architect for distributed systems project",
            "International consulting firm needs business development manager",
            "E-commerce platform looking for senior backend developer with microservices",
            "Fintech startup needs compliance officer with regulatory experience",
            "Gaming company seeking Unity developer with 4+ years experience",
            "Pharmaceutical research position for computational biologist with PhD",
            "Manufacturing company needs process engineer with Lean Six Sigma",
            "Educational technology startup seeking full-stack developer",
            "Renewable energy company needs electrical engineer with solar experience"
        ]
    
    def _generate_ground_truth(self) -> List[Dict[str, bool]]:
        """为测试样本生成标准答案（人工标注的正确答案）"""
        # 对应_generate_test_samples()中每句话的5个维度标准答案
        # 维度顺序: Location, Job Title, Years of Experience, Industry, Skills
        return [
            # "We are looking for a backend engineer for our financial department with more than 5 years experience"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": True, "Skills": False},
            # "Senior Python developer needed in New York with machine learning expertise"
            {"Location": True, "Job Title": True, "Years of Experience": True, "Industry": False, "Skills": True},
            # "Remote DevOps engineer with AWS certification and 3+ years experience required"
            {"Location": True, "Job Title": True, "Years of Experience": True, "Industry": False, "Skills": True},
            # "Data scientist with PhD in statistics for pharmaceutical company in Boston"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Frontend developer for startup in San Francisco, React experience preferred"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Looking for Java developers with Spring Boot experience in London"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Senior AI engineer needed for tech company with computer vision skills"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": True, "Skills": True},
            # "Product manager with 7+ years experience in fintech industry"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": True, "Skills": False},
            # "Full-stack developer position available in Berlin, remote work possible"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": False},
            # "Cybersecurity analyst needed with CISSP certification and 5 years experience"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": False, "Skills": True},
            # "UX designer for e-commerce platform in Seattle, portfolio required"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": False},
            # "Database administrator with Oracle expertise for healthcare company"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Cloud architect position in Singapore with Azure and GCP experience"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Mobile app developer needed with Flutter and React Native skills"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Business analyst for consulting firm in Chicago with SQL knowledge"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Network engineer with Cisco certification for telecom company"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "QA engineer position available with automation testing experience"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Technical writer needed for software company with API documentation skills"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Solutions architect role in Toronto with microservices experience"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Site reliability engineer needed with Kubernetes and Docker expertise"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Marketing manager position in Austin with digital marketing background"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "HR specialist needed for startup with talent acquisition experience"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Financial analyst role available with CPA certification preferred"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Operations manager needed in Denver with supply chain experience"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Legal counsel position for technology company with IP law background"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Sales engineer needed with technical background in software industry"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Research scientist position available with machine learning PhD"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Project manager role in Miami with PMP certification required"
            {"Location": True, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Customer success manager needed with SaaS platform experience"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": False},
            # "Strategy consultant position available with MBA from top university"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Backend engineer for fintech startup"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": False},
            # "Senior developer needed"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": False, "Skills": False},
            # "Looking for Python programmers"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Remote work opportunity"
            {"Location": True, "Job Title": False, "Years of Experience": False, "Industry": False, "Skills": False},
            # "5+ years experience required"
            {"Location": False, "Job Title": False, "Years of Experience": True, "Industry": False, "Skills": False},
            # "New York based position"
            {"Location": True, "Job Title": False, "Years of Experience": False, "Industry": False, "Skills": False},
            # "Startup environment"
            {"Location": False, "Job Title": False, "Years of Experience": False, "Industry": True, "Skills": False},
            # "Machine learning skills"
            {"Location": False, "Job Title": False, "Years of Experience": False, "Industry": False, "Skills": True},
            # "Full-time position"
            {"Location": False, "Job Title": False, "Years of Experience": False, "Industry": False, "Skills": False},
            # "Competitive salary offered"
            {"Location": False, "Job Title": False, "Years of Experience": False, "Industry": False, "Skills": False},
            # "Healthcare company seeking data analyst with 3 years experience in Chicago"
            {"Location": True, "Job Title": True, "Years of Experience": True, "Industry": True, "Skills": False},
            # "Seeking experienced software architect for distributed systems project"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": False, "Skills": True},
            # "International consulting firm needs business development manager"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": False},
            # "E-commerce platform looking for senior backend developer with microservices"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": True, "Skills": True},
            # "Fintech startup needs compliance officer with regulatory experience"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Gaming company seeking Unity developer with 4+ years experience"
            {"Location": False, "Job Title": True, "Years of Experience": True, "Industry": True, "Skills": True},
            # "Pharmaceutical research position for computational biologist with PhD"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Manufacturing company needs process engineer with Lean Six Sigma"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True},
            # "Educational technology startup seeking full-stack developer"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": False},
            # "Renewable energy company needs electrical engineer with solar experience"
            {"Location": False, "Job Title": True, "Years of Experience": False, "Industry": True, "Skills": True}
        ]
    
    def single_analysis_test(self, text: str, tagger: CandidateTagger) -> Dict[str, Any]:
        """单次分析测试"""
        start_time = time.time()
        
        try:
            result = tagger.analyze_text(text)
            end_time = time.time()
            
            return {
                "success": result["success"],
                "duration": end_time - start_time,
                "text_length": len(text),
                "result": result.get("result"),
                "usage": result.get("usage", {}),
                "error": result.get("error") if not result["success"] else None
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "duration": end_time - start_time,
                "text_length": len(text),
                "result": None,
                "usage": {},
                "error": str(e)
            }
    
    def concurrent_test(
        self, 
        total_samples: int = 100, 
        concurrent_limit: int = 20,
        model: str = "gpt-4.1-nano-2025-04-14",
        provider: str = "openai",
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        并发测试
        
        Args:
            total_samples: 总测试样本数
            concurrent_limit: 并发限制数量
            model: 使用的模型
            provider: LLM提供商 ("openai", "perplexity", "groq")
            temperature: 温度参数
            
        Returns:
            测试结果字典
        """
        print(f"🚀 开始性能测试")
        print(f"📊 配置: {total_samples} 样本, 最大并发 {concurrent_limit}")
        print(f"🤖 提供商: {provider}, 模型: {model}, 温度: {temperature}")
        print("-" * 60)
        
        # 创建标签器实例
        tagger = CandidateTagger(
            model=model,
            provider=provider,
            temperature=temperature,
            max_tokens=500
        )
        
        # 准备测试数据 - 循环使用样本直到达到总数
        test_texts = []
        for i in range(total_samples):
            test_texts.append(self.test_samples[i % len(self.test_samples)])
        
        # 记录开始时间
        overall_start = time.time()
        results = []
        
        # 使用线程池进行并发测试
        with ThreadPoolExecutor(max_workers=concurrent_limit) as executor:
            # 提交所有任务
            future_to_text = {
                executor.submit(self.single_analysis_test, text, tagger): text 
                for text in test_texts
            }
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_text):
                result = future.result()
                results.append(result)
                completed += 1
                
                # 显示进度
                if completed % 10 == 0 or completed == total_samples:
                    progress = (completed / total_samples) * 100
                    print(f"进度: {completed}/{total_samples} ({progress:.1f}%)")
        
        overall_end = time.time()
        
        # 分析结果
        return self._analyze_results(results, overall_end - overall_start, concurrent_limit, model, provider)
    
    def _calculate_accuracy_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算准确性指标"""
        ground_truth = self._generate_ground_truth()
        successful_results = [r for r in results if r["success"]]
        
        # 初始化统计变量
        total_predictions = 0
        correct_predictions = 0
        dimension_stats = {
            "Location": {"correct": 0, "total": 0, "precision": 0, "recall": 0, "f1": 0},
            "Job Title": {"correct": 0, "total": 0, "precision": 0, "recall": 0, "f1": 0},
            "Years of Experience": {"correct": 0, "total": 0, "precision": 0, "recall": 0, "f1": 0},
            "Industry": {"correct": 0, "total": 0, "precision": 0, "recall": 0, "f1": 0},
            "Skills": {"correct": 0, "total": 0, "precision": 0, "recall": 0, "f1": 0}
        }
        
        for i, result in enumerate(successful_results):
            if not result.get("result") or i >= len(ground_truth):
                continue
                
            gt_sample = ground_truth[i % len(ground_truth)]
            predicted_result = result["result"]["result"]
            
            # 转换预测结果为字典格式便于比较
            predicted_dict = {}
            for item in predicted_result:
                predicted_dict[item["label"]] = item["containsCriteria"]
            
            # 计算每个维度的准确性
            for dimension in dimension_stats.keys():
                gt_value = gt_sample.get(dimension, False)
                pred_value = predicted_dict.get(dimension, False)
                
                total_predictions += 1
                dimension_stats[dimension]["total"] += 1
                
                if gt_value == pred_value:
                    correct_predictions += 1
                    dimension_stats[dimension]["correct"] += 1
        
        # 计算每个维度的精确率、召回率和F1分数
        for dimension, stats in dimension_stats.items():
            if stats["total"] > 0:
                # 计算该维度的混淆矩阵统计
                tp = 0  # True Positive
                fp = 0  # False Positive  
                tn = 0  # True Negative
                fn = 0  # False Negative
                
                for i, result in enumerate(successful_results):
                    if not result.get("result") or i >= len(ground_truth):
                        continue
                        
                    gt_sample = ground_truth[i % len(ground_truth)]
                    predicted_result = result["result"]["result"]
                    predicted_dict = {item["label"]: item["containsCriteria"] for item in predicted_result}
                    
                    gt_value = gt_sample.get(dimension, False)
                    pred_value = predicted_dict.get(dimension, False)
                    
                    if gt_value and pred_value:
                        tp += 1
                    elif not gt_value and pred_value:
                        fp += 1
                    elif not gt_value and not pred_value:
                        tn += 1
                    elif gt_value and not pred_value:
                        fn += 1
                
                # 计算指标
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                stats["precision"] = precision
                stats["recall"] = recall
                stats["f1"] = f1
                stats["accuracy"] = stats["correct"] / stats["total"]
        
        overall_accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        return {
            "overall_accuracy": overall_accuracy,
            "total_predictions": total_predictions,
            "correct_predictions": correct_predictions,
            "dimension_metrics": dimension_stats
        }
    
    def _analyze_results(self, results: List[Dict[str, Any]], total_time: float, concurrent_limit: int, model: str, provider: str) -> Dict[str, Any]:
        """分析测试结果"""
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]
        
        # 时间统计
        durations = [r["duration"] for r in successful_results]
        text_lengths = [r["text_length"] for r in results]
        
        # Token使用统计
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        
        for r in successful_results:
            usage = r.get("usage", {})
            total_tokens += usage.get("total_tokens", 0)
            prompt_tokens += usage.get("prompt_tokens", 0)
            completion_tokens += usage.get("completion_tokens", 0)
        
        # 维度分析统计
        dimension_stats = {
            "Location": 0,
            "Job Title": 0,
            "Years of Experience": 0,
            "Industry": 0,
            "Skills": 0
        }
        
        for r in successful_results:
            if r["result"] and "result" in r["result"]:
                for item in r["result"]["result"]:
                    if item.get("containsCriteria"):
                        dimension_stats[item["label"]] += 1
        
        # 计算准确性指标
        accuracy_metrics = self._calculate_accuracy_metrics(results)
        
        return {
            "test_config": {
                "total_samples": len(results),
                "concurrent_limit": concurrent_limit,
                "total_time": total_time,
                "model": model,
                "provider": provider,
                "ground_truth_samples": len(self._generate_ground_truth())
            },
            "accuracy_metrics": accuracy_metrics,
            "performance_metrics": {
                "success_count": len(successful_results),
                "failure_count": len(failed_results),
                "success_rate": len(successful_results) / len(results) * 100,
                "average_duration": statistics.mean(durations) if durations else 0,
                "median_duration": statistics.median(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
                "requests_per_second": len(results) / total_time,
                "successful_requests_per_second": len(successful_results) / total_time
            },
            "token_usage": {
                "total_tokens": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "average_total_tokens": total_tokens / len(successful_results) if successful_results else 0,
                "average_prompt_tokens": prompt_tokens / len(successful_results) if successful_results else 0,
                "average_completion_tokens": completion_tokens / len(successful_results) if successful_results else 0
            },
            "content_analysis": {
                "average_text_length": statistics.mean(text_lengths),
                "dimension_frequencies": dimension_stats,
                "dimension_percentages": {
                    k: v / len(successful_results) * 100 if successful_results else 0 
                    for k, v in dimension_stats.items()
                }
            },
            "errors": [r["error"] for r in failed_results] if failed_results else []
        }
    
    def print_results(self, results: Dict[str, Any]):
        """打印测试结果"""
        config = results["test_config"]
        perf = results["performance_metrics"]
        tokens = results["token_usage"]
        content = results["content_analysis"]
        accuracy = results.get("accuracy_metrics", {})
        
        print("\n" + "="*60)
        print("📈 性能测试结果")
        print("="*60)
        
        print(f"\n🔧 测试配置:")
        print(f"  总样本数: {config['total_samples']}")
        print(f"  并发限制: {config['concurrent_limit']}")
        print(f"  总耗时: {config['total_time']:.2f}秒")
        print(f"  模型: {config.get('model', 'N/A')}")
        print(f"  提供商: {config.get('provider', 'N/A')}")
        print(f"  标准答案样本数: {config.get('ground_truth_samples', 'N/A')}")
        
        print(f"\n⚡ 性能指标:")
        print(f"  成功请求: {perf['success_count']}")
        print(f"  失败请求: {perf['failure_count']}")
        print(f"  成功率: {perf['success_rate']:.1f}%")
        print(f"  平均响应时间: {perf['average_duration']:.3f}秒")
        print(f"  中位数响应时间: {perf['median_duration']:.3f}秒")
        print(f"  最快响应: {perf['min_duration']:.3f}秒")
        print(f"  最慢响应: {perf['max_duration']:.3f}秒")
        print(f"  响应时间标准差: {perf['std_duration']:.3f}秒")
        print(f"  总QPS: {perf['requests_per_second']:.2f}")
        print(f"  成功QPS: {perf['successful_requests_per_second']:.2f}")
        
        # 显示准确性指标
        if accuracy:
            print(f"\n🎯 准确性指标:")
            print(f"  总体准确率: {accuracy.get('overall_accuracy', 0):.1%}")
            print(f"  正确预测数: {accuracy.get('correct_predictions', 0)}")
            print(f"  总预测数: {accuracy.get('total_predictions', 0)}")
            
            print(f"\n📊 各维度详细指标:")
            dimension_metrics = accuracy.get('dimension_metrics', {})
            for dim, metrics in dimension_metrics.items():
                print(f"  {dim}:")
                print(f"    准确率: {metrics.get('accuracy', 0):.1%}")
                print(f"    精确率: {metrics.get('precision', 0):.1%}")
                print(f"    召回率: {metrics.get('recall', 0):.1%}")
                print(f"    F1分数: {metrics.get('f1', 0):.3f}")
        
        print(f"\n🪙 Token使用统计:")
        print(f"  总Token数: {tokens['total_tokens']}")
        print(f"  Prompt Tokens: {tokens['prompt_tokens']}")
        print(f"  Completion Tokens: {tokens['completion_tokens']}")
        print(f"  平均每请求Token: {tokens['average_total_tokens']:.1f}")
        print(f"  平均Prompt Token: {tokens['average_prompt_tokens']:.1f}")
        print(f"  平均Completion Token: {tokens['average_completion_tokens']:.1f}")
        
        print(f"\n📋 内容分析:")
        print(f"  平均文本长度: {content['average_text_length']:.1f}字符")
        print(f"  维度检测频率:")
        for dim, percentage in content["dimension_percentages"].items():
            print(f"    {dim}: {percentage:.1f}%")
        
        if results["errors"]:
            print(f"\n❌ 错误信息:")
            for error in set(results["errors"]):  # 去重
                print(f"  - {error}")


if __name__ == "__main__":
    # 可调整的测试参数
    TOTAL_SAMPLES = 100          # 总测试样本数
    CONCURRENT_LIMIT = 20        # 每秒并发数量
    
    # 选择提供商和模型 - 可以轻松切换
    PROVIDER = "gemini"            # 提供商: "openai", "perplexity", "groq", "ali", "gemini"
    
    # 根据提供商选择模型
    if PROVIDER == "openai":
        MODEL = "gpt-4.1-nano-2025-04-14"
    elif PROVIDER == "perplexity":
        MODEL = "llama-3.1-sonar-small-128k-online"
    elif PROVIDER == "groq":
        MODEL = "llama-3.1-70b-versatile"  # 或者其他Groq模型
        # 其他可选Groq模型:
        # "llama-3.1-8b-instant"
        # "llama-3.2-1b-preview" 
        # "llama-3.2-3b-preview"
        # "mixtral-8x7b-32768"
        # "gemma-7b-it"
        # "gemma2-9b-it"
    elif PROVIDER == "ali":
        MODEL = "deepseek-v3"  # 或者其他Ali模型
        # 其他可选Ali模型:
        # "qwen-max"
        # "qwen-turbo"
        # "qwen-plus"
        # "qwen-long"
        # "qwen2.5-72b-instruct"
        # "qwen2.5-32b-instruct"
    elif PROVIDER == "gemini":
        MODEL = "gemini-2.5-flash-lite"  # 或者其他Gemini模型
        # 其他可选Gemini模型:
        # "gemini-1.5-pro"
        # "gemini-1.5-flash"
        # "gemini-1.0-pro"
    
    TEMPERATURE = 0.0            # 温度参数
    
    # 创建测试实例
    test_runner = CandidateTaggerPerformanceTest()
    
    # 运行测试
    try:
        results = test_runner.concurrent_test(
            total_samples=TOTAL_SAMPLES,
            concurrent_limit=CONCURRENT_LIMIT,
            model=MODEL,
            provider=PROVIDER,
            temperature=TEMPERATURE
        )
        
        # 打印结果
        test_runner.print_results(results)
        
        # 保存结果到文件
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"performance_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 结果已保存到: {results_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行出error: {e}")
        import traceback
        traceback.print_exc()