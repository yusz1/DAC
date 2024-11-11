import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import List, Tuple, Optional
from scr.plot_base import PlotStyle, PlotHelper
from scr.data_processing import (get_data_columns, preprocess_data,
                               calculate_out_of_spec)

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
