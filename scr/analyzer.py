import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from .data_processing import clean_data, get_data_columns, preprocess_data
from .plotting import plot_distributions, plot_boxplots, plot_single_distribution
from .utils import get_output_dir

def setup_matplotlib():
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

def create_output_dirs(data_path):
    output_dir = get_output_dir(data_path)
    single_dist_dir = os.path.join(output_dir, 'single_distributions')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(single_dist_dir, exist_ok=True)
    return output_dir, single_dist_dir

def generate_plots(df, data_columns, data_df, lsl_values, usl_values, output_dir, single_dist_dir, config):
    # 绘制总体分布图
    plot_distributions(df, config)
    plt.savefig(os.path.join(output_dir, 'distribution_plots.png'))
    plt.close()
    
    # 绘制单个分布图
    for col in data_columns:
        fig = plot_single_distribution(data_df, col, lsl_values, usl_values, config)
        plt.savefig(os.path.join(single_dist_dir, f'{col}.png'))
        plt.close(fig)
    
    # 绘制箱线图
    plot_boxplots(df, config)
    plt.savefig(os.path.join(output_dir, 'boxplot.png'))
    plt.close()

def analyze_data(data_path: str, config: object) -> str:
    """执行完整的数据分析流程"""
    setup_matplotlib()
    
    print("读取数据文件...")
    df = pd.read_excel(data_path)
    print(f"数据加载成功！从: {data_path}")
    
    print("\n=== 数据检查阶段 ===")
    print("数据形状:", df.shape)
    print("\n检查数据中的无效值...")
    # 对所有数值列进行检查
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    print("数值列:", numeric_columns.tolist())
    
    has_invalid_data = False
    for col in numeric_columns:
        mask = ~np.isfinite(df[col])
        if mask.any():
            has_invalid_data = True
            print(f"在列 {col} 中发现无效值，无效值总数: {mask.sum()}")
    
    if not has_invalid_data:
        print("未发现无效值")
    
    print("\n=== 开始数据处理 ===")
    print("正在清理数据...")
    df = clean_data(df, config)
    
    output_dir, single_dist_dir = create_output_dirs(data_path)
    data_columns = get_data_columns(df, config)
    print("\n处理的数据列:", data_columns)
    
    data_df, lsl_values, usl_values = preprocess_data(df)
    
    print("\n开始绘制分析图...")
    generate_plots(df, data_columns, data_df, lsl_values, usl_values, 
                  output_dir, single_dist_dir, config)
    
    return output_dir 