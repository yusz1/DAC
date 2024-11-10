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
    """绘制单个分布图的通用逻辑"""
    sns.histplot(data=data, kde=True, ax=ax)
    legend_handles = []
    
    if config.PLOT['show_lsl'] and lsl is not None:
        line = ax.axvline(x=lsl, color='r', linestyle='--', 
                         label=f'LSL: {format_number(lsl)}')
        legend_handles.append(line)
    if config.PLOT['show_usl'] and usl is not None:
        line = ax.axvline(x=usl, color='r', linestyle='--', 
                         label=f'USL: {format_number(usl)}')
        legend_handles.append(line)
    
    total_count = len(data)
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    cpk = calculate_cpk(data, usl, lsl)
    out_of_spec_count = calculate_out_of_spec_column(data, lsl, usl)
    
    stats_text = f'Test: {total_count}\nNG: {out_of_spec_count}'
    stats_text += f'\nMean: {mean:.3f}\nStd: {std:.3f}'
    if cpk is not None:
        stats_text += f'\nCpk: {cpk:.3f}'
        
    ax.text(0.95, 0.95, stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
            fontsize=fontsize)
    
    title = f"{config.PLOT['title_prefix']} {col}" if config.PLOT['title_prefix'] else col
    ax.set_title(title)
    if legend_handles:
        ax.legend(handles=legend_handles, loc='upper left', fontsize=fontsize)
    
    return legend_handles

def plot_distributions(df: pd.DataFrame, config: object) -> Figure:
    """绘制正态分布图"""
    data_columns = get_data_columns(df, config)
    data_df, lsl_values, usl_values = preprocess_data(df)
    
    total_count, total_out_of_spec_count = calculate_out_of_spec(
        data_df, data_columns, lsl_values, usl_values
    )
    
    fig = plt.figure(figsize=config.PLOT['distribution']['figsize'])
    
    for i, col in enumerate(data_columns, 1):
        ax = fig.add_subplot(5, 4, i)
        data = data_df[col].astype(float)
        lsl = float(lsl_values[col]) if lsl_values is not None else None
        usl = float(usl_values[col]) if usl_values is not None else None
        
        plot_distribution_common(ax, data, col, lsl, usl, config, fontsize='x-small')
    
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
    """绘制单个正态分布图"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    data = data_df[col].astype(float)
    lsl = float(lsl_values[col]) if lsl_values is not None else None
    usl = float(usl_values[col]) if usl_values is not None else None
    
    plot_distribution_common(ax, data, col, lsl, usl, config, fontsize='small')
    
    plt.tight_layout()
    return fig

def plot_boxplots(df: pd.DataFrame, config: object) -> Tuple[Figure, Axes]:
    """绘制箱线图"""
    data_columns = get_data_columns(df, config)
    data_df, lsl_values, usl_values = preprocess_data(df)
    
    total_count, out_of_spec_count = calculate_out_of_spec(
        data_df, data_columns, lsl_values, usl_values
    )
    
    fig, ax = plt.subplots(figsize=config.PLOT['boxplot']['figsize'])
    
    first_column = data_columns[0]
    plot_title = '_'.join(first_column.split('_')[:-1])
    
    if config.PLOT['title_prefix']:
        plot_title = f"{config.PLOT['title_prefix']} {plot_title}"
    
    ax.text(0.02, 1.01, f'Test:{total_count}  NG:{out_of_spec_count}',
            transform=ax.transAxes,
            verticalalignment='bottom',
            fontsize='large',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    flierprops = dict(marker='+', markerfacecolor='black', markersize=4)
    sns.boxplot(data=data_df[data_columns], ax=ax, flierprops=flierprops)

    x_labels = [col.split('_')[-1] for col in data_columns]
    ax.set_xticklabels(x_labels)
    ax.set_title(plot_title)
    
    ymin, ymax = ax.get_ylim()
    y_range = ymax - ymin
    
    for col_idx, col in enumerate(data_columns):
        data = data_df[col].astype(float)
        lsl = float(lsl_values[col]) if lsl_values is not None else None
        usl = float(usl_values[col]) if usl_values is not None else None
        
        cpk = calculate_cpk(data, usl, lsl)
        if cpk is not None:
            ax.text(col_idx, ymax + y_range * 0.02, f'{cpk:.3f}',
                   horizontalalignment='center',
                   verticalalignment='bottom',
                   fontsize='small')
        
        median = np.median(data)
        ax.text(col_idx, median, f'{median:.3f}',
                horizontalalignment='center',
                verticalalignment='center',
                fontsize='x-small',
                color='white',
                bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', pad=0.1))
    
    ax.set_ylim(ymin, ymax + y_range * 0.05)
    
    labeled_values = set()
    for col_idx, col in enumerate(data_columns):
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