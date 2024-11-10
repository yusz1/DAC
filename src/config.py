import os

class Config:
    # 输入文件的绝对路径（这个路径应该由用户提供）
    INPUT_PATH = r"D:\Projects\data_analysis\data\input.xlsx"  # 示例路径，实际使用时需要替换
    
    # 根据输入文件路径动态生成输出路径
    @classmethod
    def get_output_dir(cls):
        """获取输出目录（与输入文件同目录）"""
        return os.path.join(os.path.dirname(cls.INPUT_PATH), "output")
    
    @classmethod
    def get_distribution_dir(cls):
        """获取分布图目录"""
        return os.path.join(cls.get_output_dir(), "distribution")
    
    @classmethod
    def print_paths(cls):
        """打印路径信息"""
        print("\n路径信息:")
        print(f"输入文件: {cls.INPUT_PATH}")
        print(f"输出目录: {cls.get_output_dir()}")
        print(f"分布图目录: {cls.get_distribution_dir()}\n")
    
    # 图形显示配置
    SHOW_LSL = True      # 是否显示下限规格线
    SHOW_USL = True      # 是否显示上限规格线
    TITLE_PREFIX = "SFR Analysis - "  # 图表标题的前缀
    
    # 数据处理配置
    REMOVE_DUPLICATES = False  # 是否移除重复的SN数据
    
    # 数据列过滤配置：指定要分析的列名模式
    COLUMN_PATTERNS = [
        "S_NearSfr_Center",  # Center相关的列
        "S_NearSfr_0.5",     # 0.5相关的列
        "S_NearSfr_0.8"      # 0.8相关的列
    ]
    
    # 图形样式配置
    FIGURE_SIZE = (15, 10)        # 主图形的大小
    DISTRIBUTION_FIGURE_SIZE = (8, 6)  # 单个分布图的大小
    DPI = 300                     # 图片分辨率
    
    # CPK计算配置
    CPK_THRESHOLD = 1.33          # CPK警戒值
