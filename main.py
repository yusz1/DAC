from scr.utils import check_path
from scr.analyzer import analyze_data
import matplotlib.pyplot as plt
import config
import time
import warnings

def main():
    start_time = time.time()
    
    # 让 finite values 警告只显示一次
    warnings.filterwarnings('once', message='posx and posy should be finite values')
    # 添加matplotlib的warning过滤
    plt.rcParams.update({'figure.max_open_warning': 0})
    
    try:
        data_path = check_path(config.DATA['path'])
        output_dir = analyze_data(data_path, config)
        
        elapsed_time = time.time() - start_time
        print(f"分析完成！结果已保存到 {output_dir}")
        print(f"运行时间: {elapsed_time:.2f}秒")
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        raise
    finally:
        # 确保所有图表都被关闭
        plt.close('all')

if __name__ == "__main__":
    main()
