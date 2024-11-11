import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from scr.data_processing import (get_data_columns, preprocess_data,
                            calculate_cpk, calculate_out_of_spec,
                            calculate_out_of_spec_column)
from scr.utils import format_number
from dataclasses import field

@dataclass
class PlotStyle:
    """绘图样式配置"""
    fontsize: str = 'x-small'
    bbox_style: Dict = field(default_factory=lambda: dict(
        facecolor='white', alpha=0.8, edgecolor='none'
    ))
    lsl_style: Dict = field(default_factory=lambda: dict(
        color='r', linestyle='--'
    ))
    usl_style: Dict = field(default_factory=lambda: dict(
        color='r', linestyle='--'
    ))
    flierprops: Dict = field(default_factory=lambda: dict(
        marker='+', markerfacecolor='black', markersize=4
    ))
    median_style: Dict = field(default_factory=lambda: dict(
        color='white',
        bbox=dict(facecolor='black', alpha=0.6, edgecolor='none', pad=0.1)
    ))


class PlotHelper:
    """绘图辅助类"""
    @staticmethod
    def add_limit_lines(ax: Axes, col_idx: int, lsl: float, usl: float, 
                       config: object, style: PlotStyle) -> set:
        """添加限制线并返回标记的值集合"""
        labeled_values = set()
        
        # 添加LSL限制线
        if config.PLOT['show_lsl'] and lsl is not None:
            ax.hlines(y=lsl, xmin=col_idx-0.4, xmax=col_idx+0.4,
                     colors='r', linestyles='--')
            if lsl not in labeled_values:
                ax.text(col_idx, lsl, f'LSL: {format_number(lsl)}',
                       color='r', verticalalignment='bottom',
                       fontsize=style.fontsize)
                labeled_values.add(lsl)
        
        # 添加USL限制线
        if config.PLOT['show_usl'] and usl is not None:
            ax.hlines(y=usl, xmin=col_idx-0.4, xmax=col_idx+0.4,
                     colors='r', linestyles='--')
            if usl not in labeled_values:
                ax.text(col_idx, usl, f'USL: {format_number(usl)}',
                       color='r', verticalalignment='top',
                       fontsize=style.fontsize)
                labeled_values.add(usl)
        
        return labeled_values

    @staticmethod
    def add_statistics(ax: Axes, data: pd.Series, lsl: Optional[float], 
                      usl: Optional[float], style: PlotStyle) -> str:
        """添加统计信息并返回统计文本"""
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

    @staticmethod
    def setup_distribution_plot(ax: Axes, data: pd.Series, col: str,
                              lsl: Optional[float], usl: Optional[float],
                              config: object, style: PlotStyle) -> List:
        """通用的分布图设置逻辑"""
        sns.histplot(data=data, kde=True, ax=ax)
        legend_handles = []
        
        # 添加限制线和图例
        if config.PLOT['show_lsl'] and lsl is not None:
            line = ax.axvline(x=lsl, label=f'LSL: {format_number(lsl)}', 
                            **style.lsl_style)
            legend_handles.append(line)
        if config.PLOT['show_usl'] and usl is not None:
            line = ax.axvline(x=usl, label=f'USL: {format_number(usl)}', 
                            **style.usl_style)
            legend_handles.append(line)
        
        # 添加统计信息
        stats_text = PlotHelper.add_statistics(ax, data, lsl, usl, style)
        ax.text(0.95, 0.95, stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                bbox=style.bbox_style,
                fontsize=style.fontsize)
        
        # 设置标题和图例
        title = f"{config.PLOT['title_prefix']} {col}" if config.PLOT['title_prefix'] else col
        ax.set_title(title)
        if legend_handles:
            ax.legend(handles=legend_handles, loc='upper left', 
                     fontsize=style.fontsize)
        
        return legend_handles

    @staticmethod
    def setup_boxplot(ax: Axes, data_df: pd.DataFrame, data_columns: List[str],
                     lsl_values: Optional[pd.Series], usl_values: Optional[pd.Series],
                     config: object, style: PlotStyle):
        """通用的箱线图设置逻辑"""
        ymin, ymax = ax.get_ylim()
        y_range = ymax - ymin
        
        for col_idx, col in enumerate(data_columns):
            data = data_df[col].astype(float)
            lsl = float(lsl_values[col]) if lsl_values is not None else None
            usl = float(usl_values[col]) if usl_values is not None else None
            
            # 添加统计信息
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
                   fontsize=style.fontsize,
                   **style.median_style)
            
            # 添加限制线
            if lsl_values is not None or usl_values is not None:
                PlotHelper.add_limit_lines(ax, col_idx, lsl, usl, config, style)
        
        ax.set_ylim(ymin, ymax + y_range * 0.05)


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


class GroupBoxPlot:
    """分组箱线图类"""
    def __init__(self, style: PlotStyle = PlotStyle()):
        self.style = style

    def create_single_column(self, df: pd.DataFrame, group_by: str, config: object) -> Tuple[Figure, Axes]:
        """创建单列分组箱线图"""
        data_columns = get_data_columns(df, config)
        data_df, lsl_values, usl_values = preprocess_data(df)
        
        spec_mask = df['SN'].isin(['LSL', 'USL'])
        actual_data = df[~spec_mask].copy()
        
        fig, ax = plt.subplots()
        
        # 绘制箱线图
        sns.boxplot(data=actual_data, y=data_columns[0], x=group_by,
                   ax=ax, flierprops=self.style.flierprops)
        
        # 设置标题
        title = f"{config.PLOT['title_prefix']} {data_columns[0]}" if config.PLOT['title_prefix'] else data_columns[0]
        ax.set_title(title)
        
        # 添加限制线
        if lsl_values is not None and config.PLOT['show_lsl']:
            lsl = float(lsl_values[data_columns[0]])
            ax.axhline(y=lsl, color='r', linestyle='--', label=f'LSL: {lsl:.2f}')
        
        if usl_values is not None and config.PLOT['show_usl']:
            usl = float(usl_values[data_columns[0]])
            ax.axhline(y=usl, color='r', linestyle='--', label=f'USL: {usl:.2f}')
        
        ax.legend()
        plt.tight_layout()
        return fig, ax

    def create_all_columns(self, df: pd.DataFrame, group_by: str, config: object) -> Tuple[Figure, Axes]:
        """创建所有列的分组箱线图"""
        data_columns = get_data_columns(df, config)
        data_df, lsl_values, usl_values = preprocess_data(df)
        
        spec_mask = df['SN'].isin(['LSL', 'USL'])
        actual_data = df[~spec_mask].copy()
        
        fig, ax = plt.subplots(figsize=(50, 10))
        groups = sorted(actual_data[group_by].unique())
        
        # 准备数据
        group_data = [
            actual_data[actual_data[group_by] == group][data_columns]
            for group in groups
        ]
        
        # 设置箱线图位置
        positions = np.arange(len(data_columns))
        width = 0.8 / len(groups)
        
        # 为每个组绘制箱线图
        for i, (group, data) in enumerate(zip(groups, group_data)):
            pos = positions + (i - len(groups)/2 + 0.5) * width
            ax.boxplot([data[col].values for col in data_columns],
                      positions=pos,
                      widths=width,
                      flierprops=self.style.flierprops,
                      patch_artist=True,
                      boxprops=dict(facecolor=f'C{i}', alpha=0.5),
                      labels=['' for _ in data_columns],
                      medianprops=dict(color='black'))
        
        # 添加限制线和标签
        self._add_limit_lines(ax, data_columns, lsl_values, usl_values, config)
        
        # 设置图表属性
        self._setup_plot_properties(ax, positions, data_columns, groups, config)
        
        plt.tight_layout()
        return fig, ax

    def _add_limit_lines(self, ax: Axes, data_columns: List[str],
                        lsl_values: Optional[pd.Series],
                        usl_values: Optional[pd.Series],
                        config: object):
        """添加限制线"""
        if lsl_values is not None and config.PLOT['show_lsl']:
            for i, col in enumerate(data_columns):
                lsl = float(lsl_values[col])
                ax.hlines(y=lsl, xmin=i-0.4, xmax=i+0.4,
                         colors='r', linestyles='--')
                ax.text(i, lsl, f'LSL: {lsl:.2f}',
                       color='r', verticalalignment='bottom')
        
        if usl_values is not None and config.PLOT['show_usl']:
            for i, col in enumerate(data_columns):
                usl = float(usl_values[col])
                ax.hlines(y=usl, xmin=i-0.4, xmax=i+0.4,
                         colors='r', linestyles='--')
                ax.text(i, usl, f'USL: {usl:.2f}',
                       color='r', verticalalignment='top')

    def _setup_plot_properties(self, ax: Axes, positions: np.ndarray,
                             data_columns: List[str], groups: List,
                             config: object):
        """设置图表属性"""
        # 设置x轴刻度和标签
        ax.set_xticks(positions)
        x_labels = [col.split('_')[-1] for col in data_columns]
        ax.set_xticks(range(len(x_labels)))  # 先设置刻度位置
        ax.set_xticklabels(x_labels)         # 再设置刻度标签
        
        # 设置标题
        first_column = data_columns[0]
        plot_title = '_'.join(first_column.split('_')[:-1])
        if config.PLOT['title_prefix']:
            plot_title = f"{config.PLOT['title_prefix']} {plot_title}"
        
        # 设置图表属性
        ax.set_title(plot_title)
        ax.set_ylabel('Value')
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        
        # 添加图例
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=f'C{i}', alpha=0.5)
            for i in range(len(groups))
        ]
        ax.legend(legend_elements, groups, loc='upper right')

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

def plot_group_boxplots(df: pd.DataFrame, group_by: str, config: object) -> Tuple[Figure, Axes]:
    """绘制分组箱线图"""
    plotter = GroupBoxPlot()
    return plotter.create_single_column(df, group_by, config)

def plot_all_columns_by_group(df: pd.DataFrame, group_by: str, config: object) -> Tuple[Figure, Axes]:
    """在同一图中绘制所有数据列的分组箱线图"""
    plotter = GroupBoxPlot()
    return plotter.create_all_columns(df, group_by, config)
