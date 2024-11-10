import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from .data_processing import clean_data, get_data_columns, preprocess_data
from .plotting import plot_distributions, plot_boxplots, plot_single_distribution, plot_group_boxplots
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
    
    # 首先生成整体分析图
    print("\n=== 生成整体分析图 ===")
    data_df, lsl_values, usl_values = preprocess_data(df)
    generate_plots(df, data_columns, data_df, lsl_values, usl_values,
                  output_dir, single_dist_dir, config)
    
    # 然后检查是否需要生成分组分析图
    group_config = config.DATA_PROCESSING.get('group_analysis', {})
    print("\n=== 检查分组分析配置 ===")
    print(f"group_config: {group_config}")
    
    if group_config.get('enabled', False):
        print("分组分析已启用")
        group_by = group_config.get('group_by')
        plot_types = group_config.get('plot_types', {})
        print(f"分组列: {group_by}")
        
        if group_by and group_by in df.columns:
            # 分离规格数据和实际数据
            spec_mask = df['SN'].isin(['LSL', 'USL'])
            spec_data = df[spec_mask]
            actual_data = df[~spec_mask]
            groups = actual_data[group_by].unique()
            print(f"发现的{group_by}组: {groups}")
            
            plt.ioff()  # 关闭交互模式
            try:
                # 1. 生成分组分布图
                if plot_types.get('distribution', True):
                    print(f"\n=== 生成{group_by}分组分布图 ===")
                    for group_name in groups:
                        group_data = pd.concat([
                            spec_data,
                            actual_data[actual_data[group_by] == group_name]
                        ])
                        group_output_dir = os.path.join(output_dir, f"{group_by}_{group_name}")
                        group_single_dist_dir = os.path.join(group_output_dir, 'single_distributions')
                        os.makedirs(group_output_dir, exist_ok=True)
                        os.makedirs(group_single_dist_dir, exist_ok=True)
                        
                        print(f"\n处理 {group_by}: {group_name}")
                        data_df, lsl_values, usl_values = preprocess_data(group_data)
                        generate_plots(group_data, data_columns, data_df, lsl_values, usl_values,
                                    group_output_dir, group_single_dist_dir, config)
                
                # 2. 生成分组箱线图
                if plot_types.get('boxplot', True):
                    print(f"\n=== 生成{group_by}分组箱线图 ===")
                    for group_name in groups:
                        group_data = pd.concat([
                            spec_data,
                            actual_data[actual_data[group_by] == group_name]
                        ])
                        group_output_dir = os.path.join(output_dir, f"{group_by}_{group_name}")
                        os.makedirs(group_output_dir, exist_ok=True)
                        
                        print(f"\n处理 {group_by}: {group_name}")
                        data_df, lsl_values, usl_values = preprocess_data(group_data)
                        fig, ax = plot_boxplots(group_data, config)
                        plt.savefig(os.path.join(group_output_dir, 'boxplot.png'))
                        plt.close(fig)
                
                # 3. 生成分组对比图
                if plot_types.get('group_compare', True):
                    print(f"\n=== 生成{group_by}分组对比图 ===")
                    group_plots_dir = os.path.join(output_dir, f'{group_by}_comparison')
                    os.makedirs(group_plots_dir, exist_ok=True)
                    
                    for col in data_columns:
                        print(f"\n处理列: {col}")
                        fig, ax = plot_group_boxplots(df[['SN', group_by, col]], group_by, config)
                        output_path = os.path.join(group_plots_dir, f'{col}_group_comparison.png')
                        fig.savefig(output_path)
                        plt.close(fig)
                        print(f"已保存分组对比图: {output_path}")
                
            finally:
                plt.ion()  # 恢复交互模式
                
        else:
            print(f"警告: 未找到分组列 {group_by}")
    else:
        print("分组分析未启用")
    
    return output_dir 