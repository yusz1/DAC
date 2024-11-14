# 基础配置
PLOT = {
    'show_lsl': True,  # 是否显示LSL线
    'show_usl': False,  # 是否显示USL线
    'title_prefix': '',  # 标题前缀，如果不为空则会添加到标题前
    'distribution': {
        'figsize': (25, 15),
        'subplot_layout': (5, 4)
    },
    'boxplot': {
        'figsize': (20, 10)
    },
    'enable_distribution': True,    # 控制是否生成分布图
    'enable_boxplot': False,        # 控制是否生成箱线图
    'enable_group_boxplot': False,  # 控制是否生成分组箱线图
    'enable_all_columns_compare': False,  # 控制是否生成整体分组对比图
    'enable_correlation': False,  # 控制是否生成相关性分析图
}

# 数据配置
DATA = {
    'path': r'D:\Projects\data_analysis\data\test_data.xlsx'
}

# 输出配置
OUTPUT = {
    'subfolder': 'output',
    'correlation_dir': 'correlation_analysis'  # 相关性分析图的输出目录
}

# 数据预处理配置
DATA_PROCESSING = {
    'remove_duplicates': False,
    'remove_null': True,
    'remove_invalid': True,
    'group_analysis': {
        'enabled': True,           # 是否启用分组分析
        'group_by': 'Line',        # 分组列名
        # 'plot_types': {
        #     'distribution': True,   # 是否生成分组分布图
        #     'boxplot': True,       # 是否生成分组箱线图
        #     'group_compare': True,  # 是否生成分组对比图
        #     'all_columns_compare': True  # 是否生成所有列的整体分组对比图
        # }
    }
}

# 数据列配置
DATA_COLUMNS = {
    'patterns': [  # 数据列的匹配模式列表
        # 可以添加更多的模式
    ],
    'exclude_patterns': [  # 需要排除的列模式（如果有的话）
          # 例如: 'Test_', 'Temp_' 等
    ],
    'skip_columns': 5,  # 跳过前5列，其余列作为数据列
    'selection_mode': 'pattern'  # 'pattern' 或 'skip'，用于选择数据列的方式
} 