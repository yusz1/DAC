from scr.utils import check_path
from scr.analyzer import analyze_data
import config
import time
import warnings

def main():
    start_time = time.time()
    
    # 开启所有警告
    warnings.filterwarnings('always')
    # 将警告转换为异常，这样我们就能捕获到具体位置
    warnings.filterwarnings('error')
    
    try:
        data_path = check_path(config.DATA['path'])
        output_dir = analyze_data(data_path, config)
        
        elapsed_time = time.time() - start_time
        print(f"分析完成！结果已保存到 {output_dir}")
        print(f"运行时间: {elapsed_time:.2f}秒")
        
    except Warning as w:
        print(f"警告发生位置: {w.__traceback__.tb_frame.f_code.co_filename}")
        print(f"行号: {w.__traceback__.tb_lineno}")
        print(f"警告信息: {str(w)}")
        raise
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
