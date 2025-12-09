# -*- coding: utf-8 -*-
"""
DNNGP训练曲线可视化工具
可视化训练过程中的Loss、MAE、MSE等指标
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def plot_training_history(csv_path, output_dir=None, show_plot=True):
    """
    绘制训练历史曲线
    
    参数:
        csv_path: Modelhistory.csv文件路径
        output_dir: 图片保存目录，如果为None则保存到csv文件所在目录
        show_plot: 是否显示图片
    """
    # 读取CSV文件
    print(f"读取文件: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(csv_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取文件名前缀（用于保存图片）
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('DNNGP训练过程可视化', fontsize=16, fontweight='bold')
    
    # 1. Loss曲线
    ax1 = axes[0, 0]
    ax1.plot(df['epoch'], df['loss'], 'b-', linewidth=2, label='训练集Loss')
    ax1.plot(df['epoch'], df['val_loss'], 'r-', linewidth=2, label='验证集Loss')
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Loss', fontsize=12)
    ax1.set_title('Loss曲线', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 标注最小值
    min_train_loss = df['loss'].min()
    min_val_loss = df['val_loss'].min()
    min_train_epoch = df.loc[df['loss'].idxmin(), 'epoch']
    min_val_epoch = df.loc[df['val_loss'].idxmin(), 'epoch']
    ax1.scatter([min_train_epoch], [min_train_loss], color='blue', s=100, zorder=5)
    ax1.scatter([min_val_epoch], [min_val_loss], color='red', s=100, zorder=5)
    ax1.annotate(f'最小训练Loss: {min_train_loss:.4f}\nEpoch: {int(min_train_epoch)}',
                xy=(min_train_epoch, min_train_loss),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                fontsize=9)
    
    # 2. MAE曲线
    ax2 = axes[0, 1]
    ax2.plot(df['epoch'], df['mae'], 'b-', linewidth=2, label='训练集MAE')
    ax2.plot(df['epoch'], df['val_mae'], 'r-', linewidth=2, label='验证集MAE')
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('MAE (Mean Absolute Error)', fontsize=12)
    ax2.set_title('MAE曲线', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 标注最小值
    min_val_mae = df['val_mae'].min()
    min_val_mae_epoch = df.loc[df['val_mae'].idxmin(), 'epoch']
    ax2.scatter([min_val_mae_epoch], [min_val_mae], color='red', s=100, zorder=5)
    ax2.annotate(f'最小验证MAE: {min_val_mae:.4f}\nEpoch: {int(min_val_mae_epoch)}',
                xy=(min_val_mae_epoch, min_val_mae),
                xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                fontsize=9)
    
    # 3. MSE曲线
    ax3 = axes[1, 0]
    ax3.plot(df['epoch'], df['mse'], 'b-', linewidth=2, label='训练集MSE')
    ax3.plot(df['epoch'], df['val_mse'], 'r-', linewidth=2, label='验证集MSE')
    ax3.set_xlabel('Epoch', fontsize=12)
    ax3.set_ylabel('MSE (Mean Squared Error)', fontsize=12)
    ax3.set_title('MSE曲线', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # 4. 过拟合分析
    ax4 = axes[1, 1]
    # 计算训练集和验证集loss的差异
    loss_gap = df['val_loss'] - df['loss']
    ax4.plot(df['epoch'], loss_gap, 'g-', linewidth=2)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax4.set_xlabel('Epoch', fontsize=12)
    ax4.set_ylabel('验证Loss - 训练Loss', fontsize=12)
    ax4.set_title('过拟合分析 (正值表示过拟合)', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 标注过拟合程度
    final_gap = loss_gap.iloc[-1]
    max_gap = loss_gap.max()
    gap_color = 'red' if final_gap > 0.1 else 'orange' if final_gap > 0.05 else 'green'
    ax4.fill_between(df['epoch'], 0, loss_gap, where=(loss_gap > 0), 
                     alpha=0.3, color='red', label='过拟合区域')
    ax4.fill_between(df['epoch'], 0, loss_gap, where=(loss_gap <= 0), 
                     alpha=0.3, color='green', label='良好拟合区域')
    ax4.legend(fontsize=10)
    
    # 添加统计信息文本框
    textstr = f'训练统计信息:\n'
    textstr += f'总Epoch数: {len(df)}\n'
    textstr += f'最终训练Loss: {df["loss"].iloc[-1]:.4f}\n'
    textstr += f'最终验证Loss: {df["val_loss"].iloc[-1]:.4f}\n'
    textstr += f'最小验证Loss: {min_val_loss:.4f} (Epoch {int(min_val_epoch)})\n'
    textstr += f'最小验证MAE: {min_val_mae:.4f} (Epoch {int(min_val_mae_epoch)})\n'
    textstr += f'过拟合程度: {final_gap:.4f}'
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    fig.text(0.02, 0.02, textstr, fontsize=10, verticalalignment='bottom',
            bbox=props)
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.96])
    
    # 保存图片
    output_path = os.path.join(output_dir, f'{base_name}_curves.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"图片已保存到: {output_path}")
    
    # 保存高分辨率PDF版本
    pdf_path = os.path.join(output_dir, f'{base_name}_curves.pdf')
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"PDF版本已保存到: {pdf_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    # 打印详细统计信息
    print("\n" + "="*60)
    print("训练统计摘要".center(60))
    print("="*60)
    print(f"{'指标':<20} {'最小值':<15} {'最终值':<15} {'最优Epoch':<10}")
    print("-"*60)
    print(f"{'训练Loss':<20} {df['loss'].min():<15.4f} {df['loss'].iloc[-1]:<15.4f} {int(df.loc[df['loss'].idxmin(), 'epoch']):<10}")
    print(f"{'验证Loss':<20} {df['val_loss'].min():<15.4f} {df['val_loss'].iloc[-1]:<15.4f} {int(df.loc[df['val_loss'].idxmin(), 'epoch']):<10}")
    print(f"{'训练MAE':<20} {df['mae'].min():<15.4f} {df['mae'].iloc[-1]:<15.4f} {int(df.loc[df['mae'].idxmin(), 'epoch']):<10}")
    print(f"{'验证MAE':<20} {df['val_mae'].min():<15.4f} {df['val_mae'].iloc[-1]:<15.4f} {int(df.loc[df['val_mae'].idxmin(), 'epoch']):<10}")
    print(f"{'训练MSE':<20} {df['mse'].min():<15.4f} {df['mse'].iloc[-1]:<15.4f} {int(df.loc[df['mse'].idxmin(), 'epoch']):<10}")
    print(f"{'验证MSE':<20} {df['val_mse'].min():<15.4f} {df['val_mse'].iloc[-1]:<15.4f} {int(df.loc[df['val_mse'].idxmin(), 'epoch']):<10}")
    print("="*60)
    
    # 生成单独的Loss曲线（用于论文或报告）
    fig2, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.plot(df['epoch'], df['loss'], 'b-', linewidth=2.5, label='Training Loss', marker='o', markersize=4, markevery=max(1, len(df)//20))
    ax.plot(df['epoch'], df['val_loss'], 'r-', linewidth=2.5, label='Validation Loss', marker='s', markersize=4, markevery=max(1, len(df)//20))
    ax.set_xlabel('Epoch', fontsize=14, fontweight='bold')
    ax.set_ylabel('Loss', fontsize=14, fontweight='bold')
    ax.set_title('Training and Validation Loss', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.tick_params(labelsize=12)
    
    # 标注最佳点
    ax.scatter([min_val_epoch], [min_val_loss], color='red', s=150, zorder=5, marker='*')
    ax.annotate(f'Best: {min_val_loss:.4f}',
                xy=(min_val_epoch, min_val_loss),
                xytext=(15, 15), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.8),
                fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    plt.tight_layout()
    single_loss_path = os.path.join(output_dir, f'{base_name}_loss_only.png')
    plt.savefig(single_loss_path, dpi=300, bbox_inches='tight')
    print(f"单独Loss曲线已保存到: {single_loss_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='可视化DNNGP训练曲线')
    parser.add_argument('--csv', type=str, required=True, help='Modelhistory CSV文件路径')
    parser.add_argument('--output', type=str, default=None, help='输出目录（默认为CSV文件所在目录）')
    parser.add_argument('--no-show', action='store_true', help='不显示图片，只保存')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv):
        print(f"错误: 找不到文件 {args.csv}")
    
    plot_training_history(args.csv, args.output, show_plot=not args.no_show)

