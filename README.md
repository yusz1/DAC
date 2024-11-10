# Data Analysis Tool

这是一个用于分析和可视化数据的Python工具，主要用于处理和分析SFR测试数据。

## 功能特点

- 数据加载和预处理
- 正态分布图生成（整体和单个）
- 箱线图生成
- CPK计算和显示
- 超限数据统计
- 可配置的数据处理选项

## 项目结构

data_analysis/
│
├── src/
│   ├── main.py           # 主程序入口
│   ├── data_analyzer.py  # 数据分析核心类
│   ├── config.py         # 配置文件
│   └── data_generator.py # 数据生成器
│
├── data/                 # 输入数据目录
│   └── input.xlsx       # 输入数据文件
│
├── output/              # 输出目录
│   ├── distribution/    # 单个分布图
│   ├── all_distributions.png
│   └── boxplot.png
│
├── requirements.txt     # 项目依赖
└── README.md           # 项目说明文档

## 安装说明

1. 创建虚拟环境：
```bash
python -m venv .venv
```

2. 激活虚拟环境：
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用说明

1. 配置参数：
   - 在 `src/config.py` 中设置所需的参数
   - 可配置输入输出路径、显示选项等

2. 运行程序：
```bash
python src/main.py
```

3. 查看结果：
   - 在 `output` 目录下查看生成的图表
   - 在 `output/distribution` 目录下查看单个分布图

## 配置选项

- `INPUT_PATH`: 输入数据文件路径
- `OUTPUT_DIR`: 输出目录
- `SHOW_LSL`: 是否显示LSL线
- `SHOW_USL`: 是否显示USL线
- `REMOVE_DUPLICATES`: 是否去除重复数据
- `TITLE_PREFIX`: 图表标题前缀

## 输出说明

1. 分布图：
   - 显示数据分布情况
   - 包含CPK值、样本数量、超限数量
   - LSL/USL线（可配置）

2. 箱线图：
   - 显示数据分布范围
   - 每个箱子上方显示CPK值
   - 左上角显示总样本数和超限数量

## 注意事项

- 确保输入数据格式正确
- 检查配置文件中的路径设置
- 注意数据列的命名规范

## 维护说明

- 定期更新依赖包
- 检查输入数据格式
- 备份重要数据
```
