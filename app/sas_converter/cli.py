"""
SAS转换器命令行接口
"""
import os
import sys
import argparse
from typing import Dict, List, Any
from .converter import SASConverter


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='SAS到Python代码转换工具')
    
    parser.add_argument('input_file', help='输入SAS文件路径')
    parser.add_argument('-o', '--output-dir', default='output', help='输出目录路径')
    parser.add_argument('--openai-api-key', help='OpenAI API密钥（用于分析）')
    parser.add_argument('--azure-openai-api-key', help='Azure OpenAI API密钥（用于转换）')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 '{args.input_file}' 不存在")
        sys.exit(1)
    
    # 读取SAS代码
    with open(args.input_file, 'r', encoding='utf-8') as f:
        sas_code = f.read()
    
    # 获取文件名（不含扩展名）
    base_filename = os.path.splitext(os.path.basename(args.input_file))[0]
    
    # 初始化转换器
    converter = SASConverter(
        openai_api_key=args.openai_api_key,
        azure_openai_api_key=args.azure_openai_api_key
    )
    
    print(f"开始转换SAS文件: {args.input_file}")
    
    # 转换SAS代码
    result = converter.convert(sas_code, base_filename)
    
    # 保存输出
    converter.save_output(result, args.output_dir, base_filename)
    
    print(f"转换完成，输出目录: {args.output_dir}")
    print(f"- Python代码: {os.path.join(args.output_dir, base_filename + '.py')}")
    print(f"- 依赖文件: {os.path.join(args.output_dir, 'requirements.txt')}")
    print(f"- 函数库: {os.path.join(args.output_dir, 'functions')}")
    print(f"- 分析结果: {os.path.join(args.output_dir, 'analysis')}")


if __name__ == '__main__':
    main() 