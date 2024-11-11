import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Tuple
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from .plot_base import PlotStyle
from .data_processing import get_data_columns, preprocess_data

class CorrelationPlot:
    """相关性分析图类"""
    def __init__(self, style: PlotStyle = PlotStyle()):
        self.style = style

    def plot_correlation_matrix(self, df: pd.DataFrame, config: object) -> Tuple[Figure, Axes]:
        """绘制相关性矩阵热图"""
        # 获取数据列
        data_columns = get_data_columns(df, config)
        print("\n数据列:", data_columns)
        
        data_df, _, _ = preprocess_data(df)
        print("\n数据形状:", data_df.shape)
        print("数据列类型:\n", data_df[data_columns].dtypes)
        
        # 计算相关系数
        corr = data_df[data_columns].corr()
        print("\n相关系数矩阵形状:", corr.shape)
        print("相关系数矩阵前几行:\n", corr.head())
        
        # 检查是否有无效值
        if corr.isna().any().any():
            print("\n警告：相关系数矩阵中存在无效值！")
            print("无效值位置:\n", corr.isna().sum())
        
        # 创建图形和坐标轴
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 创建掩码
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True  # 创建上三角掩码
        
        # 使用带掩码的热图
        sns.heatmap(corr, 
                   mask=mask,
                   annot=True,  # 显示相关系数
                   fmt='.2f',   # 保留两位小数
                   cmap='coolwarm',
                   vmin=-1, 
                   vmax=1,
                   center=0,
                   square=True,
                   ax=ax,
                   cbar_kws={"shrink": .5})
        
        # 设置标题
        if config.PLOT['title_prefix']:
            ax.set_title(f"{config.PLOT['title_prefix']} 相关性矩阵")
        else:
            ax.set_title('相关性矩阵')
        
        # 调整布局
        plt.tight_layout()
        return fig, ax

    def plot_item_correlations(self, df: pd.DataFrame, target_item: str, 
                             config: object) -> Tuple[Figure, Axes]:
        """绘制目标项与其他项的相关性散点图"""
        # 获取数据列
        data_columns = get_data_columns(df, config)
        if target_item not in data_columns:
            raise ValueError(f"目标项 '{target_item}' 未在数据列中找到")
        
        # 预处理数据
        data_df, _, _ = preprocess_data(df)
        
        # 计算与目标项的相关系数
        correlations = data_df[data_columns].corr()[target_item].sort_values(ascending=False)
        other_items = [item for item in correlations.index if item != target_item]
        
        # 创建子图
        n_plots = len(other_items)
        n_cols = min(3, n_plots)
        n_rows = (n_plots + n_cols - 1) // n_cols
        
        fig = plt.figure(figsize=(5*n_cols, 4*n_rows))
        
        for i, other_item in enumerate(other_items, 1):
            ax = fig.add_subplot(n_rows, n_cols, i)
            corr_value = correlations[other_item]
            
            # 绘制散点图和趋势线
            sns.regplot(data=data_df, x=target_item, y=other_item, 
                       scatter_kws={'alpha':0.5}, ax=ax)
            
            # 添加相关系数
            ax.text(0.05, 0.95, f'r = {corr_value:.3f}',
                   transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(facecolor='white', alpha=0.8))
            
            # 设置标题
            ax.set_title(f'{target_item} vs {other_item}')
        
        plt.tight_layout()
        return fig, fig.axes

def plot_correlations(df: pd.DataFrame, config: object) -> None:
    """绘制相关性分析图"""
    try:
        plotter = CorrelationPlot()
        
        # 获取输出目录
        from .utils import get_output_dir
        base_output_dir = get_output_dir(config.DATA['path'])
        correlation_dir = os.path.join(base_output_dir, 'correlation_analysis')
        print(f"\n创建输出目录: {correlation_dir}")
        os.makedirs(correlation_dir, exist_ok=True)
        
        # 创建相关性矩阵图
        print("\n开始生成相关性矩阵图...")
        fig_matrix, _ = plotter.plot_correlation_matrix(df, config)
        output_path = os.path.join(correlation_dir, '相关性矩阵.png')
        print(f"保存相关性矩阵图到: {output_path}")
        fig_matrix.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig_matrix)
        
        # 为每个数据列创建相关性分析图
        print("\n开始生成各项相关性散点图...")
        data_columns = get_data_columns(df, config)
        for target_item in data_columns:
            print(f"处理 {target_item}...")
            fig_corr, _ = plotter.plot_item_correlations(df, target_item, config)
            output_path = os.path.join(correlation_dir, f'{target_item}_相关性分析.png')
            fig_corr.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig_corr)
            
    except Exception as e:
        print(f"\n生成相关性分析图时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise