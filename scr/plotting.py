import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Optional
from .data_processing import (get_data_columns, preprocess_data, 
                            calculate_cpk, calculate_out_of_spec,
                            calculate_out_of_spec_column)
from .utils import format_number

def plot_distribution_common(ax: Axes, data: pd.Series, col: str,
                           lsl: Optional[float], usl: Optional[float],
                           config: object, fontsize: str = 'x-small') -> List:
    """绘制单个分布图的通用逻辑
    Args:
        ax: matplotlib轴对象
        data: 要绘制的数据
        col: 列名
        lsl: 下限值
        usl: 上限值
        config: 配置对象
        fontsize: 字体大小
    Returns:
        legend_handles: 图例句柄列表
    """
    # 绘制直方图和核密度估计
    sns.histplot(data=data, kde=True, ax=ax)
    legend_handles = []
    
    # 如果配置了显示LSL且存在LSL值，绘制LSL线
    if config.PLOT['show_lsl'] and lsl is not None:
        line = ax.axvline(x=lsl, color='r', linestyle='--', 
                         label=f'LSL: {format_number(lsl)}')
        legend_handles.append(line)
    # 如果配置了显示USL且存在USL值，绘制USL线
    if config.PLOT['show_usl'] and usl is not None:
        line = ax.axvline(x=usl, color='r', linestyle='--', 
                         label=f'USL: {format_number(usl)}')
        legend_handles.append(line)
    
    # 计算统计信息
    total_count = len(data)
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    cpk = calculate_cpk(data, usl, lsl)
    out_of_spec_count = calculate_out_of_spec_column(data, lsl, usl)
    
    # 构建统计信息文本
    stats_text = f'Test: {total_count}\nNG: {out_of_spec_count}'
    stats_text += f'\nMean: {mean:.3f}\nStd: {std:.3f}'
    if cpk is not None:
        stats_text += f'\nCpk: {cpk:.3f}'
    
    # 在图上添加统计信息文本框    
    ax.text(0.95, 0.95, stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
            fontsize=fontsize)
    
    # 设置图标题
    title = f"{config.PLOT['title_prefix']} {col}" if config.PLOT['title_prefix'] else col
    ax.set_title(title)
    # 如果有图例句柄，添加图例
    if legend_handles:
        ax.legend(handles=legend_handles, loc='upper left', fontsize=fontsize)
    
    return legend_handles

def plot_distributions(df: pd.DataFrame, config: object) -> Figure:
    """绘制所有列的正态分布图
    Args:
        df: 数据框
        config: 配置对象
    Returns:
        fig: matplotlib图形对象
    """
    # 获取数据列和预处理数据
    data_columns = get_data_columns(df, config)
    data_df, lsl_values, usl_values = preprocess_data(df)
    
    # 计算总体的不合格数
    total_count, total_out_of_spec_count = calculate_out_of_spec(
        data_df, data_columns, lsl_values, usl_values
    )
    
    # 创建图形对象
    fig = plt.figure(figsize=config.PLOT['distribution']['figsize'])
    
    # 为每个数据列创建子图
    for i, col in enumerate(data_columns, 1):
        ax = fig.add_subplot(5, 4, i)
        data = data_df[col].astype(float)
        lsl = float(lsl_values[col]) if lsl_values is not None else None
        usl = float(usl_values[col]) if usl_values is not None else None
        
        plot_distribution_common(ax, data, col, lsl, usl, config, fontsize='x-small')
    
    # 添加总标题
    fig.suptitle(f'Test:{total_count}  NG:{total_out_of_spec_count}', 
                 y=0.995,
                 fontsize='large',
                 bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    return fig

def plot_single_distribution(data_df: pd.DataFrame, col: str,
                           lsl_values: Optional[pd.Series],
                           usl_values: Optional[pd.Series],
                           config: object) -> Figure:
    """绘制单个正态分布图
    Args:
        data_df: 数据框
        col: 要绘制的列名
        lsl_values: 下限值Series
        usl_values: 上限值Series
        config: 配置对象
    Returns:
        fig: matplotlib图形对象
    """
    # 创建单个图形和轴对象
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 转换数据类型并获取限值
    data = data_df[col].astype(float)
    lsl = float(lsl_values[col]) if lsl_values is not None else None
    usl = float(usl_values[col]) if usl_values is not None else None
    
    # 使用通用绘图函数绘制分布图
    plot_distribution_common(ax, data, col, lsl, usl, config, fontsize='small')
    
    plt.tight_layout()
    return fig

def plot_boxplots(df: pd.DataFrame, config: object) -> Tuple[Figure, Axes]:
    """绘制箱线图
    Args:
        df: 数据框
        config: 配置对象
    Returns:
        fig: matplotlib图形对象
        ax: matplotlib轴对象
    """
    # 获取数据列和预处理数据
    data_columns = get_data_columns(df, config)
    data_df, lsl_values, usl_values = preprocess_data(df)
    
    # 计算总体的不合格数
    total_count, out_of_spec_count = calculate_out_of_spec(
        data_df, data_columns, lsl_values, usl_values
    )
    
    # 创建图形和轴对象
    fig, ax = plt.subplots(figsize=config.PLOT['boxplot']['figsize'])
    
    # 从第一列名称中提取基础标题
    first_column = data_columns[0]
    plot_title = '_'.join(first_column.split('_')[:-1])
    
    # 添加配置的标题前缀
    if config.PLOT['title_prefix']:
        plot_title = f"{config.PLOT['title_prefix']} {plot_title}"
    
    # 添加测试和不合格数量信息
    ax.text(0.02, 1.01, f'Test:{total_count}  NG:{out_of_spec_count}',
            transform=ax.transAxes,
            verticalalignment='bottom',
            fontsize='large',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    # 设置异常值点的样式并绘制箱线图
    flierprops = dict(marker='+', markerfacecolor='black', markersize=4)
    sns.boxplot(data=data_df[data_columns], ax=ax, flierprops=flierprops)

    # 设置x轴标签
    x_labels = [col.split('_')[-1] for col in data_columns]
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels)
    ax.set_title(plot_title)
    
    # 获取y轴范围
    ymin, ymax = ax.get_ylim()
    y_range = ymax - ymin
    
    # 为每列添加Cpk和中位数标签
    for col_idx, col in enumerate(data_columns):
        data = data_df[col].astype(float)
        lsl = float(lsl_values[col]) if lsl_values is not None else None
        usl = float(usl_values[col]) if usl_values is not None else None
        
        # 添加Cpk值
        cpk = calculate_cpk(data, usl, lsl)
        if cpk is not None:
            ax.text(col_idx, ymax + y_range * 0.02, f'{cpk:.3f}',
                   horizontalalignment='center',
                   verticalalignment='bottom',
                   fontsize='small')
        
        # 添加中位数标签
        median = np.median(data)
        ax.text(col_idx, median, f'{median:.3f}',
                horizontalalignment='center',
                verticalalignment='center',
                fontsize='x-small',
                color='white',
                bbox=dict(facecolor='black', alpha=0.8, edgecolor='none', pad=0.2),
                zorder=10)
    
    # 调整y轴范围以容纳标签
    ax.set_ylim(ymin, ymax + y_range * 0.05)
    
    # 添加LSL和USL线
    labeled_values = set()  # 用于跟踪已标记的值，避免重复标记
    for col_idx, col in enumerate(data_columns):
        # 添加LSL线和标签
        if lsl_values is not None and config.PLOT['show_lsl']:
            lsl = float(lsl_values[col])
            ax.hlines(y=lsl, xmin=col_idx-0.4, xmax=col_idx+0.4, 
                     colors='r', linestyles='--')
            if lsl not in labeled_values:
                ax.text(col_idx, lsl, f'{lsl:.2f}', 
                       horizontalalignment='right', 
                       verticalalignment='bottom',
                       color='red')
                labeled_values.add(lsl)
                
        # 添加USL线和标签
        if usl_values is not None and config.PLOT['show_usl']:
            usl = float(usl_values[col])
            ax.hlines(y=usl, xmin=col_idx-0.4, xmax=col_idx+0.4, 
                     colors='r', linestyles='--')
            if usl not in labeled_values:
                ax.text(col_idx, usl, f'{usl:.2f}', 
                       horizontalalignment='right', 
                       verticalalignment='top',
                       color='red')
                labeled_values.add(usl)

    plt.tight_layout()
    return fig, ax

def plot_group_boxplots(df: pd.DataFrame, group_by: str, config: object) -> Tuple[Figure, Axes]:
    """绘制分组箱线图"""
    # 获取数据列
    data_columns = get_data_columns(df, config)
    
    # 预处理数据
    data_df, lsl_values, usl_values = preprocess_data(df)
    
    # 分离规格数据和实际数据
    spec_mask = df['SN'].isin(['LSL', 'USL'])
    actual_data = df[~spec_mask].copy()
    
    try:
        # 创建图形和轴对象，使用计算出的大小
        fig, ax = plt.subplots()
        
        # 设置异常值点的样式
        flierprops = dict(marker='+', markerfacecolor='black', markersize=4)
        
        # 使用seaborn的boxplot，直接使用数据列
        sns.boxplot(data=actual_data, y=data_columns[0], x=group_by,
                   ax=ax, flierprops=flierprops)
        
        # 设置标题
        title = f"{config.PLOT['title_prefix']} {data_columns[0]}" if config.PLOT['title_prefix'] else data_columns[0]
        ax.set_title(title)
        
        # 添加LSL和USL线
        if lsl_values is not None and config.PLOT['show_lsl']:
            lsl = float(lsl_values[data_columns[0]])
            ax.axhline(y=lsl, color='r', linestyle='--', label=f'LSL: {lsl:.2f}')
        
        if usl_values is not None and config.PLOT['show_usl']:
            usl = float(usl_values[data_columns[0]])
            ax.axhline(y=usl, color='r', linestyle='--', label=f'USL: {usl:.2f}')
        # 添加图例
        ax.legend()
        # 调整布局
        plt.tight_layout()
        return fig, ax
        
    except Exception as e:
        print(f"\n绘制箱线图时出错:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        raise