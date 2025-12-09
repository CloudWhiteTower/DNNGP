#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HMP to VCF Converter
将Hapmap格式(HMP)的SNP数据转换为VCF格式

使用方法:
    python hmp2vcf.py input.hmp.txt output.vcf
"""

import sys
import argparse
from datetime import datetime


def parse_hmp_header(header_line):
    """解析HMP文件的表头，返回样本名列表"""
    fields = header_line.strip().split('\t')
    # HMP格式前11列是固定的: rs#, alleles, chrom, pos, strand, assembly, center, protLSID, assayLSID, panel, Qccode
    # 从第12列开始是样本名
    samples = fields[11:]
    return samples


def convert_genotype(geno, ref_allele, alt_allele):
    """
    转换基因型格式从HMP到VCF
    HMP: AA, TT, GG, CC, AT, AG, etc., NA, --
    VCF: 0/0, 0/1, 1/1, ./.
    """
    if geno == 'NA' or geno == '--' or geno == 'NN':
        return './.'
    
    # 纯合参考
    if len(geno) == 2 and geno[0] == ref_allele and geno[1] == ref_allele:
        return '0/0'
    
    # 纯合替代
    if len(geno) == 2 and geno[0] == alt_allele and geno[1] == alt_allele:
        return '1/1'
    
    # 杂合
    if len(geno) == 2:
        if (geno[0] == ref_allele and geno[1] == alt_allele) or \
           (geno[0] == alt_allele and geno[1] == ref_allele):
            return '0/1'
    
    # 其他情况标记为缺失
    return './.'


def hmp_to_vcf(hmp_file, vcf_file):
    """主转换函数"""
    print(f"正在读取HMP文件: {hmp_file}")
    
    with open(hmp_file, 'r') as hmp_in, open(vcf_file, 'w') as vcf_out:
        # 读取表头
        header_line = hmp_in.readline()
        samples = parse_hmp_header(header_line)
        
        print(f"检测到 {len(samples)} 个样本")
        
        # 写入VCF表头
        vcf_out.write("##fileformat=VCFv4.2\n")
        vcf_out.write(f"##fileDate={datetime.now().strftime('%Y%m%d')}\n")
        vcf_out.write(f"##source=hmp2vcf.py\n")
        vcf_out.write('##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">\n')
        vcf_out.write('##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">\n')
        vcf_out.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
        
        # 写入VCF列名
        vcf_out.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(samples) + "\n")
        
        # 处理每一行SNP数据
        snp_count = 0
        for line in hmp_in:
            if not line.strip():
                continue
            
            fields = line.strip().split('\t')
            
            # 提取固定字段
            snp_id = fields[0]      # rs#
            alleles = fields[1]     # alleles (e.g., "A/G")
            chrom = fields[2]       # chromosome
            pos = fields[3]         # position
            genotypes = fields[11:] # 基因型数据
            
            # 解析等位基因
            if '/' in alleles:
                allele_list = alleles.split('/')
                ref_allele = allele_list[0]
                alt_allele = allele_list[1]
            else:
                # 如果没有/分隔符，跳过该行
                print(f"警告: SNP {snp_id} 的等位基因格式不正确: {alleles}")
                continue
            
            # 转换基因型
            vcf_genotypes = []
            non_missing = 0
            alt_count = 0
            total_alleles = 0
            
            for geno in genotypes:
                vcf_gt = convert_genotype(geno, ref_allele, alt_allele)
                vcf_genotypes.append(vcf_gt)
                
                # 计算统计信息
                if vcf_gt != './.':
                    non_missing += 1
                    if vcf_gt == '0/1':
                        alt_count += 1
                        total_alleles += 2
                    elif vcf_gt == '1/1':
                        alt_count += 2
                        total_alleles += 2
                    elif vcf_gt == '0/0':
                        total_alleles += 2
            
            # 计算等位基因频率
            if total_alleles > 0:
                af = alt_count / total_alleles
            else:
                af = 0.0
            
            # 构建INFO字段
            info = f"NS={non_missing};AF={af:.4f}"
            
            # 写入VCF行
            vcf_line = f"{chrom}\t{pos}\t{snp_id}\t{ref_allele}\t{alt_allele}\t.\tPASS\t{info}\tGT\t" + "\t".join(vcf_genotypes) + "\n"
            vcf_out.write(vcf_line)
            
            snp_count += 1
            if snp_count % 1000 == 0:
                print(f"已处理 {snp_count} 个SNP...")
    
    print(f"转换完成! 共处理 {snp_count} 个SNP")
    print(f"VCF文件已保存: {vcf_file}")


def main():
    parser = argparse.ArgumentParser(
        description='将Hapmap格式(HMP)转换为VCF格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python hmp2vcf.py input.hmp.txt output.vcf
    python hmp2vcf.py maize1k.train.hmp.txt maize1k.train.vcf
        """
    )
    
    parser.add_argument('input', help='输入的HMP文件路径')
    parser.add_argument('output', help='输出的VCF文件路径')
    
    args = parser.parse_args()
    
    try:
        hmp_to_vcf(args.input, args.output)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
