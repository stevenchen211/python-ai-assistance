"""
SAS代码分析命令行接口
"""
import os
import sys
import argparse
import json
from typing import Dict, Any

from app.tasks import analyze_code, analyze_file, analyze_directory


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='SAS代码分析工具')
    
    # 创建子命令
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 分析代码命令
    code_parser = subparsers.add_parser('code', help='分析SAS代码')
    code_parser.add_argument('code', help='SAS代码')
    code_parser.add_argument('--token-size', type=int, default=4000, help='最大令牌大小')
    code_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 分析文件命令
    file_parser = subparsers.add_parser('file', help='分析SAS代码文件')
    file_parser.add_argument('file_path', help='SAS代码文件路径')
    file_parser.add_argument('--token-size', type=int, default=4000, help='最大令牌大小')
    file_parser.add_argument('--output', '-o', help='输出文件路径')
    
    # 分析目录命令
    dir_parser = subparsers.add_parser('dir', help='分析目录中的SAS代码文件')
    dir_parser.add_argument('dir_path', help='目录路径')
    dir_parser.add_argument('--pattern', default='*.sas', help='文件匹配模式')
    dir_parser.add_argument('--token-size', type=int, default=4000, help='最大令牌大小')
    dir_parser.add_argument('--output', '-o', help='输出文件路径')
    
    return parser.parse_args()


def save_result(result: Dict[str, Any], output_path: str = None):
    """保存分析结果"""
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"结果已保存到: {output_path}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """主函数"""
    args = parse_args()
    
    if args.command == 'code':
        # 分析代码
        result = analyze_code.delay(args.code, args.token_size)
        print(f"任务ID: {result.id}")
        print("任务已提交，请稍后查看结果")
        
    elif args.command == 'file':
        # 分析文件
        if not os.path.exists(args.file_path):
            print(f"错误: 文件不存在: {args.file_path}")
            sys.exit(1)
            
        result = analyze_file.delay(args.file_path, args.token_size)
        print(f"任务ID: {result.id}")
        print("任务已提交，请稍后查看结果")
        
    elif args.command == 'dir':
        # 分析目录
        if not os.path.isdir(args.dir_path):
            print(f"错误: 目录不存在: {args.dir_path}")
            sys.exit(1)
            
        result = analyze_directory.delay(args.dir_path, args.pattern, args.token_size)
        print(f"任务ID: {result.id}")
        print("任务已提交，请稍后查看结果")
        
    else:
        print("请指定命令: code, file 或 dir")
        sys.exit(1)


if __name__ == '__main__':
    main() 