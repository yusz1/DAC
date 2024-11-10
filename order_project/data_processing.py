from typing import Tuple, Optional, List, Union
import pandas as pd
import numpy as np
import config

def get_data_columns(df: pd.DataFrame, config: object) -> List[str]:
    """获取所有符合条件的数据列"""
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
        import re
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', s)]
    
    return sorted(list(all_columns), key=natural_sort_key)

def clean_data(df: pd.DataFrame, config: object) -> pd.DataFrame:
    """清理数据：移除无效值和重复值"""
    data_columns = get_data_columns(df, config)
    needed_columns = ['SN', 'Time'] + list(data_columns)
    cleaned_df = df[needed_columns]
    
    if config.DATA_PROCESSING['remove_invalid_values']:
        for col in data_columns:
            mask = cleaned_df[col] == -10001
            cleaned_df.loc[mask, col] = np.nan
            
    if config.DATA_PROCESSING['remove_duplicates']:
        if 'Time' in cleaned_df.columns:
            cleaned_df.loc[:, 'Time'] = pd.to_datetime(cleaned_df['Time'])
            
        spec_mask = cleaned_df['SN'].isin(['LSL', 'USL'])
        spec_data = cleaned_df[spec_mask]
        actual_data = cleaned_df[~spec_mask]
        
        actual_data.drop_duplicates(subset=['SN'], keep='last', inplace=True)
        cleaned_df = pd.concat([spec_data, actual_data], ignore_index=True)
    
    return cleaned_df

def preprocess_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[pd.Series], Optional[pd.Series]]:
    """预处理数据，分离测量数据和规格限"""
    data_columns = get_data_columns(df, config)
    needed_columns = ['SN'] + list(data_columns)
    
    data_df = df.loc[~df['SN'].isin(['LSL', 'USL']), needed_columns]
    lsl_values = df[df['SN'] == 'LSL'].iloc[0] if 'LSL' in df['SN'].values else None
    usl_values = df[df['SN'] == 'USL'].iloc[0] if 'USL' in df['SN'].values else None
    
    for col in data_columns:
        data_df.loc[:, col] = pd.to_numeric(data_df[col], errors='coerce')

    return data_df, lsl_values, usl_values

def calculate_out_of_spec(data_df: pd.DataFrame, data_columns: List[str], 
                         lsl_values: Optional[pd.Series], 
                         usl_values: Optional[pd.Series]) -> Tuple[int, int]:
    """计算超限数量"""
    total_count = len(data_df)
    out_of_spec_count = 0
    
    for col in data_columns:
        data = data_df[col].astype(float)
        out_of_spec = pd.Series([False] * len(data))
        
        if lsl_values is not None:
            lsl = float(lsl_values[col])
            out_of_spec |= (data < lsl)
            
        if usl_values is not None:
            usl = float(usl_values[col])
            out_of_spec |= (data > usl)
            
        out_of_spec_count += out_of_spec.sum()
    
    return total_count, out_of_spec_count

def calculate_cpk(data: Union[pd.Series, np.ndarray], 
                 usl: Optional[float] = None, 
                 lsl: Optional[float] = None) -> Optional[float]:
    """计算CPK值"""
    if usl is None and lsl is None:
        return None
        
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    
    if std == 0:
        return None
        
    cpu = (usl - mean) / (3 * std) if usl is not None else float('inf')
    cpl = (mean - lsl) / (3 * std) if lsl is not None else float('inf')
    
    if usl is None:
        return cpl
    if lsl is None:
        return cpu
        
    return min(cpu, cpl)

def calculate_out_of_spec_column(data, lsl=None, usl=None):
    """计算单列的超限数量"""
    out_of_spec = pd.Series([False] * len(data))
    
    if lsl is not None:
        out_of_spec |= (data < lsl)
        
    if usl is not None:
        out_of_spec |= (data > usl)
        
    return out_of_spec.sum() 