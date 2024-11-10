# SFR数据分析工具

一个用于分析和可视化 SFR 测试数据的 Python 工具，提供数据统计、分布分析和可视化功能。

## 主要功能

- 📊 数据分布分析
  - 正态分布图（总体和单项）
  - 箱线图展示
  - CPK 计算与显示
- 📈 数据处理
  - 异常值检测
  - 数据清洗
  - 重复值处理
- 📋 统计分析
  - 超限数据统计
  - 基础统计指标计算
  - 样本分析报告

## 快速开始

### 环境要求
- Python 3.8 或更高版本
- Windows/Linux/MacOS

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/your-username/data-analysis.git
cd data-analysis
```

2. 创建并激活虚拟环境：
```bash
# 创建虚拟环境
python -m venv .venv

# Windows激活
.venv\Scripts\activate

# Linux/MacOS激活
source .venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

### 使用方法

1. 准备数据文件：
   - 将 Excel 数据文件放入 `data` 目录
   - 确保数据格式符合要求

2. 配置参数：
   - 打开 `config.py` 文件
   - 根据需要修改配置参数

3. 运行分析：
```bash
python main.py
```

4. 查看结果：
   - 分析结果将保存在 `output` 目录
   - 包含分布图、箱线图等可视化结果

## 配置说明

### 基础配置
```python
INPUT_PATH = "data/input.xlsx"    # 输入文件路径
OUTPUT_DIR = "output"             # 输出目录
SHOW_LSL = True                   # 显示下限线
SHOW_USL = True                   # 显示上限线
```

### 数据处理选项
```python
REMOVE_DUPLICATES = True          # 去除重复值
REMOVE_OUTLIERS = False           # 去除异常值
DECIMAL_PLACES = 3                # 小数位数
```

## 输出文件说明

- `output/distribution/`：单个参数分布图
- `output/all_distributions.png`：所有参数分布总览
- `output/boxplot.png`：箱线图分析
- `output/statistics.csv`：统计数据报告

## 常见问题

1. **导入错误**
   - 检查虚拟环境是否正确激活
   - 确认所有依赖包已安装

2. **数据格式错误**
   - 确保 Excel 文件格式正确
   - 检查数据列名是否符合要求

3. **路径错误**
   - 检查配置文件中的路径设置
   - 确保输入输出目录存在

## 维护与更新

- 定期更新依赖包：
```bash
pip install --upgrade -r requirements.txt
```
- 定期备份数据和配置文件
- 检查并更新数据处理逻辑

## 贡献指南

欢迎提交问题和改进建议！
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：[your-email@example.com]
