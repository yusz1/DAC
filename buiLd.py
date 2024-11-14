import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--name=DataAnalyzer',
    '--windowed',
    '--onefile',
    '--clean',
    f'--distpath={os.path.join(current_dir, "../dist")}',
    f'--workpath={os.path.join(current_dir, "../build")}',
    '--noconfirm',
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=matplotlib',
    '--hidden-import=seaborn',
    '--hidden-import=openpyxl',
    # 只有在确实需要资源文件时才添加下面这行
    # '--add-data=resources;resources'  # Windows使用分号
])