import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from scr.utils import format_number
from scr.data_processing import calculate_cpk, calculate_out_of_spec_column

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
        """设置分布图的通用元素"""
        # 绘制直方图和密度曲线
        sns.histplot(data=data, stat='density', ax=ax)
        sns.kdeplot(data=data, ax=ax, color='red')
        
        # 获取y轴限制
        ymin, ymax = ax.get_ylim()
        
        # 添加统计信息
        stats_text = PlotHelper.add_statistics(ax, data, lsl, usl, style)
        ax.text(0.95, 0.95, stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                fontsize=style.fontsize,
                bbox=style.bbox_style)
        
        # 添加限制线
        if config.PLOT['show_lsl'] and lsl is not None:
            ax.axvline(x=lsl, **style.lsl_style)
        
        if config.PLOT['show_usl'] and usl is not None:
            ax.axvline(x=usl, **style.usl_style)
        
        # 设置标题
        ax.set_title(col.split('_')[-1])
        
        # 移除y轴标签
        ax.set_ylabel('')
        
        return [ymin, ymax]
