import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Optional
from scr.plot_base import PlotStyle, PlotHelper
from scr.data_processing import (get_data_columns, preprocess_data,
                               calculate_out_of_spec, calculate_cpk)

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
