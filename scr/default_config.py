# 默认配置文件
DATA = {
    'path': '',  # 数据文件路径
}

# 图表配置
PLOT = {
    # 基本显示配置
    'show_lsl': False,          # 显示LSL线
    'show_usl': False,          # 显示USL线
    'title_prefix': '',        # 图表标题前缀
    
    # 图表类型启用配置
    'enable_distribution': False,    # 启用分布图
    'enable_boxplot': False,        # 启用箱线图
    'enable_group_boxplot': False, # 启用分组箱线图
    'enable_all_columns_compare': False,  # 启用整体分组对比图
    'enable_correlation': False,    # 启用相关性分析图
    
    # 分布图配置
    'distribution': {
        'figsize': (25, 15),  # 图表大小
    },
    
    # 箱线图配置
    'boxplot': {
        'figsize': (20, 10),
    },
}

# 数据处理配置
DATA_PROCESSING = {
    'remove_duplicates': False,  # 是否移除重复值
    'remove_null': True,         # 是否移除空值
    'remove_invalid': True,      # 是否移除无效值
    
    # 分组分析配置
    'group_analysis': {
        'enabled': False,        # 是否启用分组分析
        'group_by': 'Line',      # 默认分组列名
    },
}