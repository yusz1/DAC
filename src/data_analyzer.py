import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from settings import Settings

class DataAnalyzer:
    def __init__(self, path_manager):
        """初始化数据分析器"""
        self.settings = Settings()
        self.path_manager = path_manager
        self.data = None
        self.specs = None
        self.measurement_columns = []
        
    def load_data(self):
        """加载并预处理数据"""
        print(">>> 读取数据文件...")
        df = pd.read_excel(self.path_manager.input_path)
        
        # 分离规格行和数据行
        self.specs = df.iloc[:2].copy()
        self.data = df.iloc[2:].copy()
        
        # 识别并转换数值列
        self.find_measurement_columns()
        print(f"发现 {len(self.measurement_columns)} 个数据列")
        
        for col in self.measurement_columns:
            print(f"处理列: {col}")
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
        # 如果配置要求去重，则根据SN去重
        original_count = len(self.data)
        if self.settings.REMOVE_DUPLICATES:
            self.data = self.data.drop_duplicates(subset=['SN'])
            print(f"去重后数据量: {len(self.data)} (原数据量: {original_count})")
        
        return f"总行数: {len(self.data)}, 数据列数: {len(self.measurement_columns)}"
            
    def find_measurement_columns(self):
        """识别需要分析的数据列"""
        # 根据配置的模式匹配列名
        self.measurement_columns = [
            col for col in self.data.columns 
            if any(pattern in col for pattern in self.settings.COLUMN_PATTERNS)
        ]
        
    def calculate_statistics(self, column):
        """计算单列的统计信息"""
        # 去除空值后的数据
        data = self.data[column].dropna()
        # 获取规格值
        lsl = self.specs.iloc[0][column]
        usl = self.specs.iloc[1][column]
        
        # 计算基本统计量
        mean = data.mean()
        std = data.std()
        
        # 计算CPK
        cpu = (usl - mean) / (3 * std) if not pd.isna(usl) else np.inf
        cpl = (mean - lsl) / (3 * std) if not pd.isna(lsl) else np.inf
        cpk = min(cpu, cpl)
        
        # 计算超限数量
        below_lsl = data[data < lsl].count() if not pd.isna(lsl) else 0
        above_usl = data[data > usl].count() if not pd.isna(usl) else 0
        out_of_spec = below_lsl + above_usl
        total = data.count()
        
        # 打印详细信息
        print(f"\n{column} 统计信息:")
        print(f"- Test: {total}")
        print(f"- NG: {out_of_spec} (LSL: {below_lsl}, USL: {above_usl})")
        print(f"- CPK: {cpk:.3f}")
        
        return {
            'mean': mean,
            'std': std,
            'cpk': cpk,
            'total': total,
            'out_of_spec': out_of_spec,
            'below_lsl': below_lsl,
            'above_usl': above_usl,
            'lsl': lsl,
            'usl': usl
        }
        
    def plot_distribution(self, save_all=True, save_individual=True):
        """控制分布图的绘制"""
        if save_all:
            print("生成综合分布图...")
            self._plot_combined_distributions()
            
        if save_individual:
            print("生成单个分布图...")
            total = len(self.measurement_columns)
            for i, col in enumerate(self.measurement_columns, 1):
                print(f"处理列 {i}/{total}: {col}")
                self._plot_individual_distributions_single(col)
                
    def _plot_combined_distributions(self):
        """在一张图上绘制所有列的分布图"""
        # 计算子图布局
        n_cols = len(self.measurement_columns)
        n_rows = (n_cols + 3) // 4  # 每行最多4个图
        
        # 创建画布和子图
        fig, axes = plt.subplots(n_rows, 4, figsize=self.settings.FIGURE_SIZE)
        axes = axes.flatten()  # 将多维数组转为一维
        
        # 绘制每个列的分布图
        for ax, col in zip(axes, self.measurement_columns):
            stats = self.calculate_statistics(col)
            self._plot_single_distribution(ax, col, stats)
            
        # 隐藏多余的子图
        for ax in axes[len(self.measurement_columns):]:
            ax.set_visible(False)
            
        plt.tight_layout()  # 调整布局
        self._save_plot('all_distributions.png')  # 保存图片
        
    def _plot_individual_distributions_single(self, column):
        """为单个列绘制分布图"""
        output_dir = Path(self.path_manager.distribution_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=self.settings.DISTRIBUTION_FIGURE_SIZE)
        stats = self.calculate_statistics(column)
        self._plot_single_distribution(ax, column, stats)
        plt.tight_layout()
        plt.savefig(output_dir / f"{column}_distribution.png", dpi=self.settings.DPI)
        plt.close()
        
    def _plot_single_distribution(self, ax, column, stats):
        """绘制单个分布图"""
        # 准备数据
        data = self.data[column].dropna()
        
        # 绘制直方图和密度曲线
        sns.histplot(data=data, kde=True, ax=ax)
        
        # 添加规格线
        if self.settings.SHOW_LSL and not pd.isna(stats['lsl']):
            ax.axvline(stats['lsl'], color='r', linestyle='--', label='LSL')
        if self.settings.SHOW_USL and not pd.isna(stats['usl']):
            ax.axvline(stats['usl'], color='r', linestyle='--', label='USL')
            
        # 设置标题为列名
        ax.set_title(f"{column}")
        
        # 添加统计信息到图表左上角
        stats_text = (
            f"Test: {stats['total']}\n"
            f"NG: {stats['out_of_spec']}\n"
            f"CPK: {stats['cpk']:.2f}"
        )
        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 添加图例
        ax.legend()
        
    def plot_boxplot(self):
        """绘制箱线图"""
        print("准备箱线图数据...")
        plt.figure(figsize=self.settings.FIGURE_SIZE)
        
        # 准备数据
        plot_data = self.data[self.measurement_columns].melt()
        
        # 绘制箱线图
        print("绘制箱线图...")
        sns.boxplot(x='variable', y='value', data=plot_data)
        
        # 添加CPK值
        print("添加统计信息...")
        for i, col in enumerate(self.measurement_columns):
            stats = self.calculate_statistics(col)
            plt.text(i, plt.ylim()[1], f'{stats["cpk"]:.2f}', 
                    horizontalalignment='center')
            
        # 添加总体统计信息到左上角
        total_samples = len(self.data)
        total_oos = sum(self.calculate_statistics(col)['out_of_spec'] 
                       for col in self.measurement_columns)
        stats_text = (
            f"Test: {total_samples}\n"
            f"NG: {total_oos}"
        )
        plt.text(0.02, 0.98, stats_text,
                transform=plt.gca().transAxes,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 设置x轴标签旋转
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图片
        self._save_plot('boxplot.png')
        
    def _save_plot(self, filename):
        """保存图片到输出目录"""
        output_path = self.path_manager.output_dir / filename
        plt.savefig(output_path, dpi=self.settings.DPI)
        plt.close()
        
    def _plot_individual_distributions(self):
        """为每列生成单独的分布图"""
        total = len(self.measurement_columns)
        for i, col in enumerate(self.measurement_columns, 1):
            fig, ax = plt.subplots(figsize=self.settings.DISTRIBUTION_FIGURE_SIZE)
            stats = self.calculate_statistics(col)
            self._plot_single_distribution(ax, col, stats)
            plt.tight_layout()
            
            # 保存到distribution目录
            output_path = self.path_manager.distribution_dir / f"{col}_distribution.png"
            plt.savefig(output_path, dpi=self.settings.DPI)
            plt.close()
            print(f"\r>>> 进度: {i}/{total}", end="")
        print()