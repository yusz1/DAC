class Settings:
    # 图形显示配置
    SHOW_LSL = True
    SHOW_USL = True
    TITLE_PREFIX = "SFR Analysis - "
    
    # 数据处理配置
    REMOVE_DUPLICATES = False
    
    # 数据列过滤配置
    COLUMN_PATTERNS = [
        "S_NearSfr_Center",
        "S_NearSfr_0.5",
        "S_NearSfr_0.8"
    ]
    
    # 图形样式配置
    FIGURE_SIZE = (15, 10)
    DISTRIBUTION_FIGURE_SIZE = (8, 6)
    DPI = 300
    
    # CPK计算配置
    CPK_THRESHOLD = 1.33 