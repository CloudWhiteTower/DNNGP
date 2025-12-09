# -*- coding: utf-8 -*-
"""
数据预处理工具 - 处理缺失值和数据对齐
"""

import pandas as pd
import pickle
import sys
import os

def clean_and_align_data(snp_file, pheno_file, output_dir):
    """
    清理并对齐SNP和表型数据
    
    参数:
        snp_file: SNP文件路径 (.pkl)
        pheno_file: 表型文件路径 (.tsv)
        output_dir: 输出目录
    """
    print("="*60)
    print("数据预处理工具".center(60))
    print("="*60)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 读取SNP数据
    print(f"\n正在读取SNP文件: {snp_file}")
    with open(snp_file, 'rb') as f:
        snp_df = pickle.load(f)
    print(f"SNP数据形状: {snp_df.shape}")
    print(f"SNP样本数: {len(snp_df)}")
    
    # 2. 读取表型数据
    print(f"\n正在读取表型文件: {pheno_file}")
    pheno_df = pd.read_csv(pheno_file, sep='\t', index_col=0)
    print(f"表型数据形状: {pheno_df.shape}")
    print(f"表型样本数: {len(pheno_df)}")
    print(f"缺失值数量: {pheno_df.isnull().sum().sum()}")
    
    # 3. 删除表型中的缺失值
    print("\n正在删除表型数据中的缺失值...")
    pheno_clean = pheno_df.dropna()
    print(f"清理后表型样本数: {len(pheno_clean)}")
    
    # 4. 找到共同样本
    print("\n正在对齐SNP和表型数据...")
    common_samples = snp_df.index.intersection(pheno_clean.index)
    print(f"共同样本数: {len(common_samples)}")
    
    if len(common_samples) == 0:
        print("\n错误: SNP和表型数据没有共同样本!")
        print(f"SNP样本示例: {list(snp_df.index[:5])}")
        print(f"表型样本示例: {list(pheno_clean.index[:5])}")
        return False
    
    # 5. 对齐数据
    snp_aligned = snp_df.loc[common_samples]
    pheno_aligned = pheno_clean.loc[common_samples]
    
    print(f"\n对齐后数据:")
    print(f"  SNP形状: {snp_aligned.shape}")
    print(f"  表型形状: {pheno_aligned.shape}")
    
    # 6. 检查数据质量
    print("\n数据质量检查:")
    snp_nan = snp_aligned.isnull().sum().sum()
    snp_inf = (snp_aligned == float('inf')).sum().sum() + (snp_aligned == float('-inf')).sum().sum()
    pheno_nan = pheno_aligned.isnull().sum().sum()
    pheno_inf = (pheno_aligned == float('inf')).sum().sum() + (pheno_aligned == float('-inf')).sum().sum()
    
    print(f"  SNP中的NaN: {snp_nan}")
    print(f"  SNP中的Inf: {snp_inf}")
    print(f"  表型中的NaN: {pheno_nan}")
    print(f"  表型中的Inf: {pheno_inf}")
    
    if snp_nan > 0 or snp_inf > 0:
        print("\n警告: SNP数据包含异常值，正在处理...")
        # 填充SNP中的NaN为0
        snp_aligned = snp_aligned.fillna(0)
        # 替换Inf为最大/最小值
        snp_aligned = snp_aligned.replace([float('inf'), float('-inf')], [snp_aligned.max().max(), snp_aligned.min().min()])
        print("  已填充SNP数据中的异常值")
    
    # 7. 打印统计信息
    print("\n表型数据统计:")
    print(pheno_aligned.describe())
    
    # 8. 保存对齐后的数据
    snp_output = os.path.join(output_dir, 'snp_aligned.pkl')
    pheno_output = os.path.join(output_dir, os.path.basename(pheno_file).replace('.tsv', '_aligned.tsv'))
    
    print(f"\n正在保存对齐后的数据...")
    with open(snp_output, 'wb') as f:
        pickle.dump(snp_aligned, f)
    pheno_aligned.to_csv(pheno_output, sep='\t')
    
    print(f"  SNP保存至: {snp_output}")
    print(f"  表型保存至: {pheno_output}")
    
    print("\n" + "="*60)
    print("数据预处理完成!".center(60))
    print("="*60)
    
    return True

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("使用方法: python data_preprocessing.py <snp.pkl> <pheno.tsv> <output_dir>")
        print("\n示例:")
        print('  python data_preprocessing.py "snp.pkl" "pheno.tsv" "aligned_data"')
        sys.exit(1)
    
    snp_file = sys.argv[1]
    pheno_file = sys.argv[2]
    output_dir = sys.argv[3]
    
    if not os.path.exists(snp_file):
        print(f"错误: SNP文件不存在: {snp_file}")
        sys.exit(1)
    
    if not os.path.exists(pheno_file):
        print(f"错误: 表型文件不存在: {pheno_file}")
        sys.exit(1)
    
    success = clean_and_align_data(snp_file, pheno_file, output_dir)
    sys.exit(0 if success else 1)
