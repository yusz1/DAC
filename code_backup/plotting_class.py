import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from ..src.data_processing import (get_data_columns, preprocess_data, 
                            calculate_cpk, calculate_out_of_spec,
                            calculate_out_of_spec_column)
from ..src.utils import format_number

@dataclass
class PlotStyle:
    """绘图样式配置"""
    fontsize: str = 'x-small'
    bbox_style: Dict = dict(facecolor='white', alpha=0.8, edgecolor='none')
    lsl_style: Dict = dict(color='r', linestyle='--')
    usl_style: Dict = dict(color='r', linestyle='--')
    flierprops: Dict = dict(marker='+', markerfacecolor='black', markersize=4)
    median_style: Dict = dict(
        color='white',
        bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', pad=0.1)
    )

class PlotHelper:
    """绘图辅助类"""
    @staticmethod
    def add_limit_lines(ax: Axes, col_idx: int, lsl: float, usl: float, 
                       config: object, style: PlotStyle) -> set:
        """添加限制线"""
        labeled_values = set()
        
        if lsl is not None and config.PLOT['show_lsl']:
            ax.hlines(y=lsl, xmin=col_idx-0.4, xmax=col_idx+0.4, 
                     **style.lsl_style)
            if lsl not in labeled_values:
                ax.text(col_idx, lsl, f'{lsl:.2f}', 
                       horizontalalignment='right', 
                       verticalalignment='bottom',
                       color='red')
                labeled_values.add(lsl)
                
        if usl is not None and config.PLOT['show_usl']:
            ax.hlines(y=usl, xmin=col_idx-0.4, xmax=col_idx+0.4, 
                     **style.usl_style)
            if usl not in labeled_values:
                ax.text(col_idx, usl, f'{usl:.2f}', 
                       horizontalalignment='right', 
                       verticalalignment='top',
                       color='red')
                labeled_values.add(usl)
                
        return labeled_values

    @staticmethod
    def add_statistics(ax: Axes, data: pd.Series, lsl: Optional[float], 
                      usl: Optional[float], style: PlotStyle) -> str:
        """添加统计信息"""
        total_count = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        cpk = calculate_cpk(data, usl, lsl)
        out_of_spec_count = calculate_out_of_spec_column(data, lsl, usl)
        
        stats_text = f'Test: {total_count}\nNG: {out_of_spec_count}'
        stats_text += f'\nMean: {mean:.3f}\nStd: {std:.3f}'
        if cpk is not None:
            stats_text += f'\nCpk: {cpk:.3f}'
            
        return stats_text

class DistributionPlot:
    """分布图类"""
    def __init__(self, style: PlotStyle = PlotStyle()):
        self.style = style

    def plot_common(self, ax: Axes, data: pd.Series, col: str,
                   lsl: Optional[float], usl: Optional[float],
                   config: object) -> List:
        """绘制通用分布图元素"""
        sns.histplot(data=data, kde=True, ax=ax)
        legend_handles = []
        
        # 添加限制线
        if config.PLOT['show_lsl'] and lsl is not None:
            line = ax.axvline(x=lsl, label=f'LSL: {format_number(lsl)}', 
                            **self.style.lsl_style)
            legend_handles.append(line)
        if config.PLOT['show_usl'] and usl is not None:
            line = ax.axvline(x=usl, label=f'USL: {format_number(usl)}', 
                            **self.style.usl_style)
            legend_handles.append(line)
        
        # 添加统计信息
        stats_text = PlotHelper.add_statistics(ax, data, lsl, usl, self.style)
        ax.text(0.95, 0.95, stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                bbox=self.style.bbox_style,
                fontsize=self.style.fontsize)
        
        # 设置标题
        title = f"{config.PLOT['title_prefix']} {col}" if config.PLOT['title_prefix'] else col
        ax.set_title(title)
        if legend_handles:
            ax.legend(handles=legend_handles, loc='upper left', 
                     fontsize=self.style.fontsize)
        
        return legend_handles

class BoxPlot:
    """箱线图类"""
    def __init__(self, style: PlotStyle = PlotStyle()):
        self.style = style

    def create(self, df: pd.DataFrame, config: object) -> Tuple[Figure, Axes]:
        """创建箱线图"""
        data_columns = get_data_columns(df, config)
        data_df, lsl_values, usl_values = preprocess_data(df)
        
        total_count, out_of_spec_count = calculate_out_of_spec(
            data_df, data_columns, lsl_values, usl_values
        )
        
        fig, ax = plt.subplots(figsize=config.PLOT['boxplot']['figsize'])
        
        # 设置标题和统计信息
        first_column = data_columns[0]
        plot_title = '_'.join(first_column.split('_')[:-1])
        if config.PLOT['title_prefix']:
            plot_title = f"{config.PLOT['title_prefix']} {plot_title}"
        
        ax.text(0.02, 1.01, f'Test:{total_count}  NG:{out_of_spec_count}',
                transform=ax.transAxes,
                verticalalignment='bottom',
                fontsize='large',
                bbox=self.style.bbox_style)
        
        # 绘制箱线图
        sns.boxplot(data=data_df[data_columns], ax=ax, 
                   flierprops=self.style.flierprops)
        
        # 设置标签
        x_labels = [col.split('_')[-1] for col in data_columns]
        ax.set_xticklabels(x_labels)
        ax.set_title(plot_title)
        
        # 添加统计信息
        self._add_statistics(ax, data_df, data_columns, lsl_values, usl_values, config)
        
        plt.tight_layout()
        return fig, ax

    def _add_statistics(self, ax: Axes, data_df: pd.DataFrame, 
                       data_columns: List[str],
                       lsl_values: Optional[pd.Series], 
                       usl_values: Optional[pd.Series],
                       config: object):
        """添加统计信息到箱线图"""
        ymin, ymax = ax.get_ylim()
        y_range = ymax - ymin
        
        for col_idx, col in enumerate(data_columns):
            data = data_df[col].astype(float)
            lsl = float(lsl_values[col]) if lsl_values is not None else None
            usl = float(usl_values[col]) if usl_values is not None else None
            
            # 添加CPK值
            cpk = calculate_cpk(data, usl, lsl)
            if cpk is not None:
                ax.text(col_idx, ymax + y_range * 0.02, f'{cpk:.3f}',
                       horizontalalignment='center',
                       verticalalignment='bottom',
                       fontsize='small')
            
            # 添加中位数
            median = np.median(data)
            ax.text(col_idx, median, f'{median:.3f}',
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=self.style.fontsize,
                    **self.style.median_style)
        
        ax.set_ylim(ymin, ymax + y_range * 0.05)
        
        # 添加限制线
        labeled_values = set()
        for col_idx, col in enumerate(data_columns):
            if lsl_values is not None or usl_values is not None:
                lsl = float(lsl_values[col]) if lsl_values is not None else None
                usl = float(usl_values[col]) if usl_values is not None else None
                labeled_values.update(
                    PlotHelper.add_limit_lines(ax, col_idx, lsl, usl, 
                                             config, self.style)
                )

# 创建绘图函数
def plot_distributions(df: pd.DataFrame, config: object) -> Figure:
    """绘制正态分布图"""
    plotter = DistributionPlot()
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
        
        plotter.plot_common(ax, data, col, lsl, usl, config)
    
    fig.suptitle(f'Test：{total_count}  NG：{total_out_of_spec_count}', 
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
    plotter = DistributionPlot(PlotStyle(fontsize='small'))
    fig, ax = plt.subplots(figsize=(8, 6))
    
    data = data_df[col].astype(float)
    lsl = float(lsl_values[col]) if lsl_values is not None else None
    usl = float(usl_values[col]) if usl_values is not None else None
    
    plotter.plot_common(ax, data, col, lsl, usl, config)
    
    plt.tight_layout()
    return fig

def plot_boxplots(df: pd.DataFrame, config: object) -> Tuple[Figure, Axes]:
    """绘制箱线图"""
    plotter = BoxPlot()
    return plotter.create(df, config)