# Data Analysis Tool

一个用于数据分析和可视化的Python工具，支持多种图表生成和数据分析功能。

## 功能特点

### 数据处理
- 自动检测和处理无效值（NaN, Inf等）
- 支持多种数据列选择模式（skip模式和pattern模式）
- 智能数据预处理和清洗

### 可视化功能
1. 整体分析
   - 总体分布图
   - 单个参数分布图
   - 整体箱线图

2. 分组分析
   - 分组分布图
   - 分组箱线图
   - 单参数分组对比图
   - 整体分组对比图

### 统计功能
- 自动计算并显示统计指标：
  - CPK值
  - 均值
  - 标准差
  - 中位数
  - 超限数量统计

### 规格线显示
- 支持LSL（下限）/USL（上限）规格线
- 智能标注规格值
- 超限数据突出显示

## 安装要求

1. Python 3.8+
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 准备数据文件（Excel格式）
2. 配置 config.py 文件：
   ```python
   DATA_PROCESSING = {
       'group_analysis': {
           'enabled': True,
           'group_by': 'Line',  # 分组列名
           'plot_types': {
               'distribution': True,  # 是否生成分布图
               'boxplot': True,      # 是否生成箱线图
               'group_compare': True, # 是否生成分组对比图
               'all_columns_compare': True  # 是否生成整体分组对比图
           }
       }
   }
   ```
3. 运行分析脚本：
```bash
python -m scr.analyzer
```

## 输出说明

程序会在数据文件同级目录下创建输出文件夹，包含：
- 总体分析图表
- 单个参数分布图
- 分组分析图表（如果启用）
- 分组对比图表（如果启用）

## 注意事项

- 确保数据文件格式正确（包含SN列和数据列）
- LSL和USL值应在数据文件中指定
- 中文字符显示需要正确配置字体
```