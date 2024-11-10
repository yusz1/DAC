import pandas as pd
import matplotlib.pyplot as plt
import os
import config
from scr.data_processing import clean_data, get_data_columns, preprocess_data
from scr.plotting import plot_distributions, plot_boxplots, plot_single_distribution
from scr.utils import get_output_dir, check_path

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def main():
    try:
        print("读取数据文件...")
        data_path = check_path(config.DATA['path'])
        df = pd.read_excel(data_path)
        print(f"数据加载成功！从: {data_path}")
        
        print("正在清理数据...")
        df = clean_data(df, config)
        
        output_dir = get_output_dir(data_path)
        single_dist_dir = os.path.join(output_dir, 'single_distributions')
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(single_dist_dir, exist_ok=True)
        
        data_columns = get_data_columns(df, config)
        data_df, lsl_values, usl_values = preprocess_data(df)
        
        print("\n开始绘制分析图...")
        plot_distributions(df, config)
        plt.savefig(os.path.join(output_dir, 'distribution_plots.png'))
        plt.close()
        
        print("正在保存单个分布图...")
        for col in data_columns:
            fig = plot_single_distribution(data_df, col, lsl_values, usl_values, config)
            plt.savefig(os.path.join(single_dist_dir, f'{col}.png'))
            plt.close(fig)
        
        plot_boxplots(df, config)
        plt.savefig(os.path.join(output_dir, 'boxplot.png'))
        plt.close()
        
        print(f"分析完成！结果已保存到 {output_dir}")
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")

if __name__ == "__main__":
    main()
