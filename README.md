# 数据分析工具

这是一个用于分析和可视化数据的Python工具，支持生成多种类型的图表和统计分析。

## 功能特点

- 支持Excel数据文件的读取和处理
- 自动检测和处理无效数据
- 支持多种图表类型：
  - 分布图（总体和单个指标）
  - 箱线图
  - 分组箱线图
  - 整体分组对比图
- 支持按组分析数据
- 自动计算统计指标（均值、标准差、CPK等）
- 支持LSL/USL规格限制的显示
- 灵活的配置系统

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置数据文件路径：
在 `config.py` 中设置数据文件路径和其他参数。

3. 运行程序：
```bash
python main.py
```

## 输出说明

程序会在数据文件所在目录创建一个输出文件夹，包含以下内容：

- `distribution_plots.png`：总体分布图
- `boxplot.png`：总体箱线图
- `single_distributions/`：单个指标的分布图
- `{group_by}_comparison/`：分组对比图
  - `{column}_group_comparison.png`：每个指标的分组对比图
  - `all_columns_comparison.png`：所有指标的分组对比图
- `{group_by}_{group_name}/`：每个分组的详细分析
  - `distribution_plots.png`：该组的分布图
  - `boxplot.png`：该组的箱线图
  - `single_distributions/`：该组单个指标的分布图

## 注意事项

1. 数据文件格式要求：
   - Excel文件需包含 'SN' 列
   - LSL和USL值需在数据中用特殊行标记（'LSL'和'USL'）

2. 图表控制：
   - 可以通过配置文件控制每种图表的生成
   - 可以单独开启或关闭任何类型的图表

3. 分组分析：
   - 需要在配置中指定正确的分组列名
   - 分组列必须存在于数据文件中

## 更新日志

### v1.1.0
- 重构代码结构，将绘图功能拆分为独立模块
- 添加了独立的图表类型控制
- 改进了错误处理和日志输出

### v1.0.0
- 初始版本发布