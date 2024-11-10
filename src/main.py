from data_analyzer import DataAnalyzer
from path_utils import PathManager
import time
from datetime import datetime
import argparse
import os

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='数据分析工具')
    parser.add_argument('--input', '-i',
                      default=r"D:\Projects\data_analysis\data\input.xlsx",  # 设置默认路径
                      help='输入文件的路径')
    args = parser.parse_args()
    
    start_time = time.time()
    print(f"\n=== 数据分析开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    try:
        # 检查输入文件是否存在
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"找不到输入文件: {args.input}")
            
        # 初始化路径管理器
        path_manager = PathManager(args.input)
        path_manager.create_directories()
        path_manager.print_paths()
        
        # 初始化分析器并处理数据
        analyzer = DataAnalyzer(path_manager)
        analyzer.load_data()
        
        print("\n>>> 生成分布图...")
        analyzer.plot_distribution(save_all=True, save_individual=True)
        
        print("\n>>> 生成箱线图...")
        analyzer.plot_boxplot()
        
        run_time = time.time() - start_time
        print(f"\n=== 分析完成 - 用时: {run_time:.1f}秒 ===\n")
        
    except Exception as e:
        print(f"\n!!! 错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()