import os
import config

def format_number(value):
    """格式化数值，去掉不必要的小数位"""
    formatted = f"{value:.3f}"
    formatted = formatted.rstrip('0')
    formatted = formatted.rstrip('.')
    return formatted

def get_output_dir(input_path: str) -> str:
    """根据输入文件路径生成输出目录路径"""
    input_dir = os.path.dirname(os.path.abspath(input_path))
    input_filename = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join(input_dir, config.OUTPUT['subfolder'], 
                             f"{input_filename}_output")
    return output_dir

def check_path(path: str) -> str:
    """验证文件路径是否存在且有效"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    if not os.path.isfile(path):
        raise ValueError(f"指定路径不是文件: {path}")
    return path
