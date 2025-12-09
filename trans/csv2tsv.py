#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV to TSV Converter
将CSV格式文件转换为TSV格式

使用方法:
    python csv2tsv.py input.csv output.tsv
"""

import sys
import argparse
import csv


def csv_to_tsv(csv_file, tsv_file):
    """主转换函数"""
    print(f"正在读取CSV文件: {csv_file}")
    
    with open(csv_file, 'r', encoding='utf-8') as csv_in, \
         open(tsv_file, 'w', encoding='utf-8', newline='') as tsv_out:
        
        # 读取CSV
        csv_reader = csv.reader(csv_in)
        
        # 写入TSV (使用制表符分隔)
        tsv_writer = csv.writer(tsv_out, delimiter='\t')
        
        row_count = 0
        for row in csv_reader:
            tsv_writer.writerow(row)
            row_count += 1
            
            if row_count % 1000 == 0:
                print(f"已处理 {row_count} 行...")
    
    print(f"转换完成! 共处理 {row_count} 行")
    print(f"TSV文件已保存: {tsv_file}")


def main():
    parser = argparse.ArgumentParser(
        description='将CSV格式转换为TSV格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python csv2tsv.py input.csv output.tsv
    python csv2tsv.py YIELD.csv YIELD.tsv
        """
    )
    
    parser.add_argument('input', help='输入的CSV文件路径')
    parser.add_argument('output', help='输出的TSV文件路径')
    
    args = parser.parse_args()
    
    try:
        csv_to_tsv(args.input, args.output)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
