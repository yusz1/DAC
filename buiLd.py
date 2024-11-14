import PyInstaller.__main__
import os

# 获取当前目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller打包配置
PyInstaller.__main__.run([
    'main.py',                # 主程序入口文件（参考 src/ui/main_window.py 中的GUI实现）
    
    # 基本配置
    '--name=DataAnalyzer',    # 生成的可执行文件名称
    '--windowed',             # 使用GUI模式，不显示控制台窗口
    '--onefile',              # 打包成单个exe文件
    '--clean',                # 清理临时文件
    
    # 输出路径配置
    f'--distpath={os.path.join(current_dir, "../dist")}',    # 指定可执行文件输出目录
    f'--workpath={os.path.join(current_dir, "../build")}',   # 指定构建过程的工作目录
    '--noconfirm',           # 覆盖现有文件，不询问
    
    # 隐式导入配置（参考 src/analyzer.py 和 src/distribution_plots.py 的导入）
    '--hidden-import=pandas',          # 数据处理库
    '--hidden-import=numpy',           # 数值计算库
    '--hidden-import=matplotlib',      # 绘图库
    '--hidden-import=seaborn',         # 统计图表库
    '--hidden-import=openpyxl',        # Excel文件处理
    
    # PyQt5相关导入（参考 src/ui/main_window.py 的GUI组件）
    '--hidden-import=PyQt5',           # PyQt5基础库
    '--hidden-import=PyQt5.QtCore',    # Qt核心功能
    '--hidden-import=PyQt5.QtGui',     # Qt GUI组件
    '--hidden-import=PyQt5.QtWidgets', # Qt窗口部件
])