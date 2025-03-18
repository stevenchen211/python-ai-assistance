#!/usr/bin/env python
"""
SAS Code Analyzer CLI

命令行工具，用于分析SAS代码中的数据库使用情况
"""
import argparse
import sys
import os
import json
from pathlib import Path

# 添加父目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.code_runner.data_source_analyzer import analyze_data_sources, analyze_databases


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分析SAS代码中的数据库使用情况')
    
    # 添加参数
    parser.add_argument('file', type=str, nargs='?', help='SAS代码文件路径 (如未提供则从标准输入读取)')
    parser.add_argument('--output', '-o', type=str, help='输出JSON文件路径 (如未提供则输出到标准输出)')
    parser.add_argument('--database-only', '-d', action='store_true', help='仅分析数据库使用情况')
    parser.add_argument('--pretty', '-p', action='store_true', help='美化输出JSON')
    
    # 解析参数
    args = parser.parse_args()
    
    # 读取SAS代码
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"错误：无法读取文件 {args.file}，{str(e)}", file=sys.stderr)
            return 1
    else:
        # 从标准输入读取
        print("请输入SAS代码，完成后按Ctrl+D (Unix) 或 Ctrl+Z (Windows) 结束：")
        code = sys.stdin.read()
    
    # 分析代码
    try:
        if args.database_only:
            result = analyze_databases(code)
        else:
            result = analyze_data_sources(code)
        
        # 如果需要美化JSON
        if args.pretty and not args.output:
            # 转换为对象，再格式化输出
            result_obj = json.loads(result)
            result = json.dumps(result_obj, indent=2, ensure_ascii=False)
        
        # 输出结果
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"分析结果已保存到：{args.output}")
            except Exception as e:
                print(f"错误：无法写入文件 {args.output}，{str(e)}", file=sys.stderr)
                return 1
        else:
            print(result)
        
        return 0
    
    except Exception as e:
        print(f"错误：分析过程中发生错误，{str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 