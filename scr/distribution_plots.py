import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Optional
from scr.plot_base import PlotStyle, PlotHelper
from scr.data_processing import (get_data_columns, preprocess_data,
                               calculate_out_of_spec, calculate_cpk,
                               calculate_out_of_spec_column)
from scr.utils import format_number
import numpy as np
import os

class DistributionPlot:
    def __init__(self, style: PlotStyle = PlotStyle()):
        self.style = style

    def plot_common(self, ax: Axes, data: pd.Series, col: str,
                   lsl: Optional[float], usl: Optional[float],
                   config: object) -> List:
        """绘制通用分布图元素"""
        return PlotHelper.setup_distribution_plot(
            ax, data, col, lsl, usl, config, self.style
        )

    @staticmethod
    def add_statistics(ax: Axes, data: pd.Series, lsl: Optional[float], 
                      usl: Optional[float], style: PlotStyle) -> str:
        # 计算基本统计量
        mean = np.mean(data)
        std = np.std(data)
        count = len(data)
        
        # 计算CPK和超限数量
        cpk = calculate_cpk(data, usl, lsl)
        out_of_spec = calculate_out_of_spec_column(data, lsl, usl)
        
        # 构建统计信息文本
        stats = [
            f'N={count}',
            f'Mean={format_number(mean)}',
            f'Std={format_number(std)}'
        ]
        
        if cpk is not None:
            stats.append(f'Cpk={format_number(cpk)}')
        
        if out_of_spec > 0:
            stats.append(f'NG={out_of_spec}')
        
        return '\n'.join(stats)

def plot_distributions(df: pd.DataFrame, config: object) -> Figure:
    """绘制正态分布图"""
    data_columns = get_data_columns(df, config)
    data_df, lsl_values, usl_values = preprocess_data(df)

    # 计算总体良率信息
    total_count, total_out_of_spec_count = calculate_out_of_spec(
        data_df, data_columns, lsl_values, usl_values
    )
    total_yield = (total_out_of_spec_count / total_count) * 100 if total_out_of_spec_count > 0 else 0
    
    # 计算需要的行数和列数
    n_cols = 4  # 保持每行4列
    n_rows = (len(data_columns) + n_cols - 1) // n_cols  # 向上取整计算行数
    
    # 创建足够大的图表
    fig = plt.figure(figsize=(
        config.PLOT['distribution']['figsize'][0],
        config.PLOT['distribution']['figsize'][1] * (n_rows / 5)  # 根据行数调整高度
    ))
    
    # 绘制每个数据列的分布图
    for i, col in enumerate(data_columns, 1):
        ax = fig.add_subplot(n_rows, n_cols, i)
        data = data_df[col].astype(float)
        lsl = float(lsl_values[col]) if lsl_values is not None else None
        usl = float(usl_values[col]) if usl_values is not None else None
        
        PlotHelper.setup_distribution_plot(ax, data, col, lsl, usl, config, PlotStyle())
     
     # 添加总标题
    fig.suptitle(f'Test: {total_count}  NG: {total_out_of_spec_count}   Rate: {total_yield:.2f}%',
                 y=0.995,
                 fontsize='large',
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    # 调整子图之间的间距
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)  # 为suptitle留出空间
    return fig

    # plotter = DistributionPlot()
    # data_columns = get_data_columns(df, config)
    # data_df, lsl_values, usl_values = preprocess_data(df)
    
    # total_count, total_out_of_spec_count = calculate_out_of_spec(
    #     data_df, data_columns, lsl_values, usl_values
    # )
    
    # fig = plt.figure(figsize=config.PLOT['distribution']['figsize'])

    # for i, col in enumerate(data_columns, 1):
    #     ax = fig.add_subplot(5, 4, i)
    #     data = data_df[col].astype(float)
    #     lsl = float(lsl_values[col]) if lsl_values is not None else None
    #     usl = float(usl_values[col]) if usl_values is not None else None
        
    #     plotter.plot_common(ax, data, col, lsl, usl, config)
    
    # fig.suptitle(f'Test：{total_count}  NG：{total_out_of_spec_count}', 
    #              y=0.995,
    #              fontsize='large',
    #              bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    # plt.tight_layout()
    # plt.subplots_adjust(top=0.95)
    # return fig

def plot_single_distribution(data_df: pd.DataFrame, col: str,
                           lsl_values: Optional[pd.Series],
                           usl_values: Optional[pd.Series],
                           config: object) -> Figure:
    """绘制单个正态分布图"""
    plotter = DistributionPlot(PlotStyle(fontsize='small'))
    fig, ax = plt.subplots(figsize=(8, 6))
    
    data = data_df[col].astype(float)
    lsl = float(lsl_values[col]) if lsl_values is not None else None
    usl = float(usl_values[col]) if usl_values is not None else None
    
    plotter.plot_common(ax, data, col, lsl, usl, config)
    
    plt.tight_layout()
    return fig

def export_statistics_to_excel(df: pd.DataFrame, config: object, output_dir: str, is_group_data: bool = False) -> None:
    """导出统计数据到Excel"""
    # 获取数据列和分组配置
    data_columns = get_data_columns(df, config)
    data_df, lsl_values, usl_values = preprocess_data(df)
    group_config = config.DATA_PROCESSING.get('group_analysis', {})
    group_by = group_config.get('group_by') if group_config.get('enabled', False) else None
    
    # 准备统计数据
    stats_data = []
    
    # 检查是否为分组数据
    if is_group_data and group_by:
        # 获取当前组的数据（排除LSL/USL行）
        actual_data = df[~df['SN'].isin(['LSL', 'USL'])]
        # 获取组名（应该只有一个唯一值）
        group_name = actual_data[group_by].unique()[0]
        for col in data_columns:
            data = data_df[col].astype(float)
            lsl = float(lsl_values[col]) if lsl_values is not None else None
            usl = float(usl_values[col]) if usl_values is not None else None
            
            # 计算统计量
            count = len(data)
            mean = np.mean(data)
            std = np.std(data)
            cpk = calculate_cpk(data, usl, lsl)
            out_of_spec = calculate_out_of_spec_column(data, lsl, usl)
            rate = f'{(out_of_spec / count * 100):.2f}%' if count > 0 else '0%'
            
            stats_data.append({
                group_by: group_name,  # 添加分组列
                'Items': col,
                'Test': count,
                'NG': out_of_spec,
                'Rate': rate,
                'LSL': lsl if lsl is not None else '',
                'USL': usl if usl is not None else '',
                'Mean': f'{mean:.3f}',
                'Std': f'{std:.3f}',
                'CPK': f'{cpk:.3f}' if cpk is not None else ''
            })
    else:
        # 非分组情况的处理
        for col in data_columns:
            data = data_df[col].astype(float)
            lsl = float(lsl_values[col]) if lsl_values is not None else None
            usl = float(usl_values[col]) if usl_values is not None else None
            
            count = len(data)
            mean = np.mean(data)
            std = np.std(data)
            cpk = calculate_cpk(data, usl, lsl)
            out_of_spec = calculate_out_of_spec_column(data, lsl, usl)
            rate = f'{(out_of_spec / count * 100):.2f}%' if count > 0 else '0%'
            
            stats_data.append({
                'Items': col,
                'Test': count,
                'NG': out_of_spec,
                'Rate': rate,
                'LSL': lsl if lsl is not None else '',
                'USL': usl if usl is not None else '',
                'Mean': f'{mean:.3f}',
                'Std': f'{std:.3f}',
                'CPK': f'{cpk:.3f}' if cpk is not None else ''
            })
    
    # 创建DataFrame并导出到Excel
    stats_df = pd.DataFrame(stats_data)
    excel_path = os.path.join(output_dir, 'statistics_summary.xlsx')
    stats_df.to_excel(excel_path, index=False)