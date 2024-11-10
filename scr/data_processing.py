from typing import Tuple, Optional, List, Union
import pandas as pd
import numpy as np
import config

def get_data_columns(df: pd.DataFrame, config: object) -> List[str]:
    """获取所有符合条件的数据列
    
    参数:
        df: 输入的数据框
        config: 配置对象，包含数据列选择的规则
        
    返回:
        符合条件的数据列名列表，按自然排序排列
    """
    all_columns = set()
    
    if config.DATA_COLUMNS['selection_mode'] == 'skip':
        skip_count = config.DATA_COLUMNS['skip_columns']
        all_columns.update(df.columns[skip_count:])
    else:
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        all_columns.update(numeric_columns)
        
        if ('exclude_patterns' in config.DATA_COLUMNS and 
            config.DATA_COLUMNS['exclude_patterns']):
            for exclude_pattern in config.DATA_COLUMNS['exclude_patterns']:
                all_columns = {col for col in all_columns 
                             if not col.startswith(exclude_pattern)}
        
        if config.DATA_COLUMNS['patterns']:
            pattern_columns = set()
            for pattern in config.DATA_COLUMNS['patterns']:
                matched_columns = [col for col in all_columns 
                                 if col.startswith(pattern)]
                pattern_columns.update(matched_columns)
            all_columns = pattern_columns
    
    def natural_sort_key(s):
        """自然排序键函数，确保Center列排在最前面
        
        参数:
            s: 列名字符串
        返回:
            排序键元组
        """
        import re
        # Center列优先排序
        if 'Center' in s:
            return ('0', *re.split('([0-9]+)', s))
        # 其他列按数字和文本分段排序
        parts = re.split('([0-9]+)', s)
        return ('1', *[int(part) if part.isdigit() else part.lower() for part in parts])
    
    # 使用自然排序对列名进行排序
    sorted_columns = sorted(list(all_columns), key=natural_sort_key)
    
    return sorted_columns

def clean_data(df: pd.DataFrame, config: object) -> pd.DataFrame:
    """清理数据：移除无效值和重复值
    
    参数:
        df: 输入的数据框
        config: 配置对象，包含数据清理的规则
        
    返回:
        cleaned_df: 清理后的数据框
    """
    # 获取需要处理的数据列
    data_columns = get_data_columns(df, config)
    
    # 分离规格数据（LSL/USL）和实际数据
    spec_mask = df['SN'].isin(['LSL', 'USL'])
    spec_data = df[spec_mask].copy()  # 规格数据
    actual_data = df[~spec_mask].copy()  # 实际测量数据
    
    print(f"处理前的行数: {len(actual_data)}")
    
    # 处理无效值（默认删除-10001）
    if config.DATA_PROCESSING.get('remove_invalid', True):
        print("正在删除-10001值...")
        actual_data[data_columns] = actual_data[data_columns].replace(-10001, np.nan)
        print(f"删除无效值后的行数: {len(actual_data)}")
    
    # 根据配置决定是否删除空值
    if config.DATA_PROCESSING['remove_null']:
        print("正在删除空值...")
        actual_data = actual_data.dropna(subset=data_columns)
        print(f"删除空值后的行数: {len(actual_data)}")
    else:
        print("保留空值...")
    
    # 处理重复值（如果配置了移除重复值）
    if config.DATA_PROCESSING['remove_duplicates']:
        # 如果存在Time列，转换为datetime类型
        if 'Time' in actual_data.columns:
            actual_data.loc[:, 'Time'] = pd.to_datetime(actual_data['Time'])
        # 根据SN列去重，保留最后一条记录
        actual_data = actual_data.drop_duplicates(subset=['SN'], keep='last')
    
    # 将处理后的规格数据和实际数据重新合并
    cleaned_df = pd.concat([spec_data, actual_data], ignore_index=True)
    
    return cleaned_df

def preprocess_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[pd.Series], Optional[pd.Series]]:
    """预处理数据，分离测量数据和规格限
    
    参数:
        df: 输入的数据框
        
    返回:
        data_df: 预处理后的测量数据
        lsl_values: 下限值，如果存在
        usl_values: 上限值，如果存在
    """
    # 获取需要处理的数据列
    data_columns = get_data_columns(df, config)
    needed_columns = ['SN'] + list(data_columns)
    
    # 分离测量数据和规格限
    data_df = df.loc[~df['SN'].isin(['LSL', 'USL']), needed_columns]
    # 提取LSL和USL值（如果存在）
    lsl_values = df[df['SN'] == 'LSL'].iloc[0] if 'LSL' in df['SN'].values else None
    usl_values = df[df['SN'] == 'USL'].iloc[0] if 'USL' in df['SN'].values else None
    
    # 将所有数据列转换为数值类型
    for col in data_columns:
        data_df.loc[:, col] = pd.to_numeric(data_df[col], errors='coerce')

    return data_df, lsl_values, usl_values

def calculate_out_of_spec(data_df: pd.DataFrame, data_columns: List[str], 
                         lsl_values: Optional[pd.Series], 
                         usl_values: Optional[pd.Series]) -> Tuple[int, int]:
    """计算超限数量
    
    参数:
        data_df: 包含测量数据的数据框
        data_columns: 需要检查的数据列列表
        lsl_values: 下限值，可选
        usl_values: 上限值，可选
        
    返回:
        total_count: 总数据点数
        out_of_spec_count: 超限数据点数
    """
    total_count = len(data_df)
    out_of_spec_count = 0
    
    for col in data_columns:
        # 将数据转换为浮点型
        data = data_df[col].astype(float)
        # 初始化超限标记数组
        out_of_spec = pd.Series([False] * len(data))
        
        # 检查下限超限
        if lsl_values is not None:
            lsl = float(lsl_values[col])
            out_of_spec |= (data < lsl)
            
        # 检查上限超限
        if usl_values is not None:
            usl = float(usl_values[col])
            out_of_spec |= (data > usl)
            
        # 累加超限数量
        out_of_spec_count += out_of_spec.sum()
    
    return total_count, out_of_spec_count

def calculate_cpk(data: Union[pd.Series, np.ndarray], 
                 usl: Optional[float] = None, 
                 lsl: Optional[float] = None) -> Optional[float]:
    """计算CPK值
    
    参数:
        data: 测量数据，可以是pandas Series或numpy数组
        usl: 上限值，可选
        lsl: 下限值，可选
        
    返回:
        cpk: CPK值，如果无法计算则返回None
    """
    # 如果没有规格限，无法计算CPK
    if usl is None and lsl is None:
        return None
        
    # 计算均值和标准差
    mean = np.mean(data)
    std = np.std(data, ddof=1)  # ddof=1使用样本标准差
    
    # 如果标准差为0，无法计算CPK
    if std == 0:
        return None
        
    # 计算CPU和CPL
    cpu = (usl - mean) / (3 * std) if usl is not None else float('inf')
    cpl = (mean - lsl) / (3 * std) if lsl is not None else float('inf')
    
    # 根据规格限情况返回CPK
    if usl is None:
        return cpl
    if lsl is None:
        return cpu
        
    return min(cpu, cpl)

def calculate_out_of_spec_column(data, lsl=None, usl=None):
    """计算单列的超限数量
    
    参数:
        data: 包含测量数据的Series或数组
        lsl: 下限值(Lower Specification Limit)，可选
        usl: 上限值(Upper Specification Limit)，可选
        
    返回:
        超出规格限的数据点数量
    """
    # 创建一个与数据等长的布尔型Series，初始值全为False
    out_of_spec = pd.Series([False] * len(data))
    
    # 如果存在下限值，检查小于下限的数据点
    # 使用 |= 运算符将结果与现有的out_of_spec合并
    if lsl is not None:
        out_of_spec |= (data < lsl)
    
    # 如果存在上限值，检查大于上限的数据点
    # 使用 |= 运算符将结果与现有的out_of_spec合并
    if usl is not None:
        out_of_spec |= (data > usl)
    
    # 返回超限的数据点总数（True值的数量）
    return out_of_spec.sum() 