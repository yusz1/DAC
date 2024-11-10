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
    }
}

# 数据配置
DATA = {
    'path': r'D:\Projects\data_analysis\data\test_data.xlsx'
}

# 输出配置
OUTPUT = {
    'subfolder': 'output'  # 输出子文件夹名
}

# 数据预处理配置
DATA_PROCESSING = {
    'remove_duplicates': True,  # 是否去除重复的SN（保留最新的记录）
    'remove_invalid_values': True,  # 是否移除无效值（空值和-10001）
}

# 数据列配置
DATA_COLUMNS = {
    'patterns': [  # 数据列的匹配模式列表
        'S_NearSfr',
        'MTF',
        'FOV',
        # 可以添加更多的模式
    ],
    'exclude_patterns': [  # 需要排除的列模式（如果有的话）
        # 例如: 'Test_', 'Temp_' 等
    ],
    'skip_columns': 5,  # 跳过前5列，其余列作为数据列
    'selection_mode': 'pattern'  # 'pattern' 或 'skip'，用于选择数据列的方式
} 