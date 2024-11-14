# -*- mode: python ; coding: utf-8 -*-

# 定义加密方式，这里不使用加密
block_cipher = None

# 定义分析对象，包含所有需要打包的内容
a = Analysis(
    ['main.py'],                # 主程序入口文件
    pathex=[],                  # 额外的导入路径
    binaries=[],               # 需要包含的二进制文件
    datas=[],                  # 需要包含的数据文件
    hiddenimports=[            # 隐式导入的包
        'pandas',              # 数据处理库
        'numpy',               # 数值计算库
        'matplotlib',          # 绘图库
        'seaborn',            # 统计图表库
        'PyQt5',              # GUI基础库
        'PyQt5.QtCore',       # Qt核心功能
        'PyQt5.QtGui',        # Qt GUI组件
        'PyQt5.QtWidgets',    # Qt窗口部件
        'openpyxl'            # Excel文件处理
    ],
    hookspath=[],              # 自定义钩子脚本路径
    hooksconfig={},            # 钩子配置
    runtime_hooks=[],          # 运行时钩子
    excludes=[],              # 要排除的模块
    win_no_prefer_redirects=False,    # Windows重定向选项
    win_private_assemblies=False,     # Windows程序集选项
    cipher=block_cipher,       # 加密设置
    noarchive=False,          # 是否不创建压缩包
)

# 创建程序包对象
pyz = PYZ(
    a.pure,                    # 纯Python模块
    a.zipped_data,            # 压缩的数据
    cipher=block_cipher        # 加密设置
)

# 创建可执行文件
exe = EXE(
    pyz,                      # 程序包对象
    a.scripts,                # 脚本
    a.binaries,              # 二进制文件
    a.zipfiles,              # 压缩文件
    a.datas,                 # 数据文件
    [],                      # 额外选项
    name='DataAnalyzer',     # 输出的exe名称
    debug=False,             # 是否开启调试
    bootloader_ignore_signals=False,  # 是否忽略引导加载器信号
    strip=False,             # 是否移除符号表
    upx=True,               # 是否使用UPX压缩
    upx_exclude=[],         # UPX排除的文件
    runtime_tmpdir=None,    # 运行时临时目录
    console=False,          # 是否显示控制台窗口
    disable_windowed_traceback=False,  # 是否禁用窗口化回溯
    target_arch=None,       # 目标架构
    codesign_identity=None, # 代码签名身份
    entitlements_file=None, # 授权文件
    icon='resources/icon.ico'  # 程序图标
)