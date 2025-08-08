#!/usr/bin/env python3
"""
LinkedIn 行业标签提取工具
从 linkedin_industries.json 文件中提取所有 label 字段
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Set

# 设置控制台编码为UTF-8
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def extract_linkedin_industry_labels(json_file_path: str = None) -> List[str]:
    """
    从 LinkedIn 行业 JSON 文件中提取所有的 label 字段
    
    Args:
        json_file_path: JSON文件路径，如果不指定则使用默认路径
    
    Returns:
        去重排序后的行业标签列表
    """
    if json_file_path is None:
        json_file_path = project_root / "document" / "linkedin_industries.json"
    else:
        json_file_path = Path(json_file_path)
    
    if not json_file_path.exists():
        raise FileNotFoundError(f"LinkedIn industries file not found: {json_file_path}")
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            industries_data = json.load(f)
        
        # 提取所有 label 字段
        labels = set()  # 使用 set 自动去重
        
        for industry in industries_data:
            if isinstance(industry, dict) and 'label' in industry:
                label = industry['label'].strip()
                if label:  # 只添加非空标签
                    labels.add(label)
        
        # 转换为排序列表
        sorted_labels = sorted(list(labels))
        
        return sorted_labels
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {json_file_path}: {e}")
    except Exception as e:
        raise Exception(f"Error reading LinkedIn industries file: {e}")


def format_industries_for_prompt(industries: List[str], format_type: str = "markdown") -> str:
    """
    将行业列表格式化为适合 prompt 的格式
    
    Args:
        industries: 行业标签列表
        format_type: 格式类型，支持 "markdown", "bullet", "line"
    
    Returns:
        格式化后的字符串
    """
    if format_type == "markdown":
        # Markdown 列表格式，适合 prompt 文件
        return "\n".join([f"- {industry}" for industry in industries])
    elif format_type == "bullet":
        # 简单的项目符号格式
        return "\n".join([f"• {industry}" for industry in industries])
    elif format_type == "line":
        # 每行一个，无符号
        return "\n".join(industries)
    else:
        raise ValueError(f"Unsupported format_type: {format_type}")


def get_industry_statistics(json_file_path: str = None) -> dict:
    """
    获取行业数据的统计信息
    
    Args:
        json_file_path: JSON文件路径
    
    Returns:
        包含统计信息的字典
    """
    if json_file_path is None:
        json_file_path = project_root / "document" / "linkedin_industries.json"
    else:
        json_file_path = Path(json_file_path)
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            industries_data = json.load(f)
        
        # 统计信息
        total_entries = len(industries_data)
        unique_labels = set()
        main_categories = set()
        
        for industry in industries_data:
            if isinstance(industry, dict):
                if 'label' in industry:
                    unique_labels.add(industry['label'].strip())
                if 'mainCategory' in industry:
                    main_categories.add(industry['mainCategory'].strip())
        
        return {
            "total_entries": total_entries,
            "unique_labels": len(unique_labels),
            "main_categories": len(main_categories),
            "main_category_list": sorted(list(main_categories))
        }
        
    except Exception as e:
        return {"error": str(e)}


def save_industries_to_file(industries: List[str], output_file: str = None, format_type: str = "markdown") -> str:
    """
    将行业列表保存到文件
    
    Args:
        industries: 行业标签列表
        output_file: 输出文件路径
        format_type: 格式类型
    
    Returns:
        保存的文件路径
    """
    if output_file is None:
        output_file = project_root / f"linkedin_industries_extracted_{format_type}.txt"
    else:
        output_file = Path(output_file)
    
    formatted_content = format_industries_for_prompt(industries, format_type)
    
    # 添加头部信息
    header = f"""# LinkedIn Industries List
# Total industries: {len(industries)}
# Format: {format_type}
# Generated from: linkedin_industries.json

"""
    
    content = header + formatted_content
    
    # 确保目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(output_file)


def main():
    """命令行接口"""
    print("[EXTRACTOR] LinkedIn 行业标签提取工具")
    print("=" * 50)
    
    try:
        # 提取行业标签
        industries = extract_linkedin_industry_labels()
        
        print(f"[SUCCESS] 成功提取 {len(industries)} 个独特的行业标签")
        
        # 显示统计信息
        stats = get_industry_statistics()
        print(f"\n[STATS] 统计信息:")
        print(f"  总条目数: {stats['total_entries']}")
        print(f"  独特标签数: {stats['unique_labels']}")
        print(f"  主要分类数: {stats['main_categories']}")
        
        # 显示前 10 个行业
        print(f"\n[PREVIEW] 前 10 个行业标签:")
        for i, industry in enumerate(industries[:10], 1):
            print(f"  {i:2d}. {industry}")
        
        if len(industries) > 10:
            print(f"  ... 还有 {len(industries) - 10} 个")
        
        # 保存到文件
        output_file = save_industries_to_file(industries, format_type="markdown")
        print(f"\n[SAVED] 行业列表已保存到: {output_file}")
        
        # 输出 Markdown 格式（用于复制到 prompt 文件）
        print(f"\n[OUTPUT] Markdown 格式 (用于 prompt 文件):")
        print("-" * 30)
        formatted_output = format_industries_for_prompt(industries, "markdown")
        print(formatted_output)
        
        return industries
        
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        return None


if __name__ == "__main__":
    result = main()
    if result is None:
        sys.exit(1)