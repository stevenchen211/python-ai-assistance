#!/usr/bin/env python
"""
SAS Code Analyzer CLI

Command line tool for analyzing database usage in SAS code
"""
import argparse
import sys
import os
import json
from pathlib import Path

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.code_runner.data_source_analyzer import analyze_data_sources, analyze_databases


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Analyze database usage in SAS code')
    
    # Add arguments
    parser.add_argument('file', type=str, nargs='?', help='SAS code file path (read from stdin if not provided)')
    parser.add_argument('--output', '-o', type=str, help='Output JSON file path (output to stdout if not provided)')
    parser.add_argument('--database-only', '-d', action='store_true', help='Only analyze database usage')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty print JSON output')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Read SAS code
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"Error: Cannot read file {args.file}, {str(e)}", file=sys.stderr)
            return 1
    else:
        # Read from stdin
        print("Please enter SAS code, press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:")
        code = sys.stdin.read()
    
    # Analyze code
    try:
        if args.database_only:
            result = analyze_databases(code)
        else:
            result = analyze_data_sources(code)
        
        # Pretty print JSON if requested
        if args.pretty and not args.output:
            # Convert to object and format output
            result_obj = json.loads(result)
            result = json.dumps(result_obj, indent=2, ensure_ascii=False)
        
        # Output results
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"Analysis results saved to: {args.output}")
            except Exception as e:
                print(f"Error: Cannot write to file {args.output}, {str(e)}", file=sys.stderr)
                return 1
        else:
            print(result)
        
        return 0
    
    except Exception as e:
        print(f"Error: An error occurred during analysis, {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 