from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QFileDialog, QLabel, QCheckBox, 
                           QGroupBox, QLineEdit, QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import os
from ..analyzer import analyze_data
import config

class AnalysisThread(QThread):
    """分析线程类"""
    finished = pyqtSignal(str)  # 发送输出目录路径
    error = pyqtSignal(str)     # 发送错误信息
    progress = pyqtSignal(str)  # 发送进度信息

    def __init__(self, config_obj):
        super().__init__()
        self.config = config_obj

    def run(self):
        try:
            output_dir = analyze_data(self.config.DATA['path'], self.config)
            self.finished.emit(output_dir)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据分析工具")
        self.setMinimumSize(800, 600)
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 添加各个配置区域
        layout.addWidget(self.create_file_section())
        layout.addWidget(self.create_plot_section())
        layout.addWidget(self.create_plot_settings_section())
        layout.addWidget(self.create_data_processing_section())
        layout.addWidget(self.create_group_analysis_section())

        # 添加运行按钮和进度条
        layout.addWidget(self.create_run_section())
        
        # 初始化配置对象
        self.config = config
        
    def create_file_section(self):
        """创建文件选择区域"""
        group = QGroupBox("文件选择")
        layout = QHBoxLayout()
        
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_file)
        
        layout.addWidget(self.file_path)
        layout.addWidget(browse_btn)
        group.setLayout(layout)
        return group
    
    def create_plot_section(self):
        """创建图表类型选择区域"""
        group = QGroupBox("图表类型")
        layout = QVBoxLayout()
        
        self.dist_check = QCheckBox("分布图")
        self.box_check = QCheckBox("箱线图")
        self.group_box_check = QCheckBox("分组箱线图")
        self.all_compare_check = QCheckBox("整体分组对比图")
        self.corr_check = QCheckBox("相关性分析图")
        
        layout.addWidget(self.dist_check)
        layout.addWidget(self.box_check)
        layout.addWidget(self.group_box_check)
        layout.addWidget(self.all_compare_check)
        layout.addWidget(self.corr_check)
        
        group.setLayout(layout)
        return group
    
    def create_plot_settings_section(self):
        """创建图表设置区域"""
        group = QGroupBox("图表设置")
        layout = QVBoxLayout()
        
        # 显示限制线设置
        limit_layout = QHBoxLayout()
        self.show_lsl_check = QCheckBox("显示LSL")
        self.show_usl_check = QCheckBox("显示USL")
        limit_layout.addWidget(self.show_lsl_check)
        limit_layout.addWidget(self.show_usl_check)
        
        # 标题前缀设置
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("标题前缀:"))
        self.title_prefix_input = QLineEdit()
        self.title_prefix_input.setPlaceholderText("输入标题前缀（可选）")
        prefix_layout.addWidget(self.title_prefix_input)
        
        layout.addLayout(limit_layout)
        layout.addLayout(prefix_layout)
        group.setLayout(layout)
        return group

    def create_data_processing_section(self):
        """创建数据处理配置区域"""
        group = QGroupBox("数据处理")
        layout = QVBoxLayout()
        
        self.remove_dup_check = QCheckBox("移除重复值")
        self.remove_null_check = QCheckBox("移除空值")
        self.remove_invalid_check = QCheckBox("移除无效值")
        
        layout.addWidget(self.remove_dup_check)
        layout.addWidget(self.remove_null_check)
        layout.addWidget(self.remove_invalid_check)
        
        group.setLayout(layout)
        return group
    
    def create_group_analysis_section(self):
        """创建分组分析配置区域"""
        group = QGroupBox("分组分析")
        layout = QVBoxLayout()
        
        self.group_enabled_check = QCheckBox("启用分组分析")
        self.group_by_input = QLineEdit()
        self.group_by_input.setPlaceholderText("输入分组列名")
        
        layout.addWidget(self.group_enabled_check)
        layout.addWidget(self.group_by_input)
        
        group.setLayout(layout)
        return group
    
    def create_run_section(self):
        """创建运行区域"""
        group = QGroupBox("运行")
        layout = QVBoxLayout()
        
        self.run_btn = QPushButton("开始分析")
        self.run_btn.clicked.connect(self.run_analysis)
        
        self.status_label = QLabel("就绪")
        
        layout.addWidget(self.run_btn)
        layout.addWidget(self.status_label)
        
        group.setLayout(layout)
        return group
    
    def init_default_states(self):
        """初始化控件的默认状态"""
        # 从配置文件加载默认值
        self.dist_check.setChecked(self.config.PLOT.get('enable_distribution', True))
        self.box_check.setChecked(self.config.PLOT.get('enable_boxplot', False))
        self.group_box_check.setChecked(self.config.PLOT.get('enable_group_boxplot', False))
        self.all_compare_check.setChecked(self.config.PLOT.get('enable_all_columns_compare', False))
        self.corr_check.setChecked(self.config.PLOT.get('enable_correlation', False))
        
        self.remove_dup_check.setChecked(self.config.DATA_PROCESSING.get('remove_duplicates', False))
        self.remove_null_check.setChecked(self.config.DATA_PROCESSING.get('remove_null', True))
        self.remove_invalid_check.setChecked(self.config.DATA_PROCESSING.get('remove_invalid', True))
        
        group_config = self.config.DATA_PROCESSING.get('group_analysis', {})
        self.group_enabled_check.setChecked(group_config.get('enabled', False))
        self.group_by_input.setText(group_config.get('group_by', 'Line'))

    def browse_file(self):
        """打开文件选择对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据文件",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.file_path.setText(file_path)
            self.config.DATA['path'] = file_path

    def run_analysis(self):
        """运行数据分析"""
        if not self.file_path.text():
            QMessageBox.warning(self, "警告", "请先选择数据文件！")
            return
        
        try:
            # 更新配置
            from .utils import update_config
            self.config = update_config(self.config, self)
            
            # 禁用运行按钮
            self.run_btn.setEnabled(False)
            self.status_label.setText("正在分析...")
            
            # 创建并启动分析线程
            self.analysis_thread = AnalysisThread(self.config)
            self.analysis_thread.finished.connect(self.analysis_completed)
            self.analysis_thread.error.connect(self.analysis_error)
            self.analysis_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析过程中出现错误：{str(e)}")
            self.run_btn.setEnabled(True)
            self.status_label.setText("分析失败")

    def analysis_completed(self, output_dir):
        """分析完成的回调函数"""
        self.run_btn.setEnabled(True)
        self.status_label.setText("分析完成")
        
        reply = QMessageBox.information(
            self,
            "完成",
            f"分析已完成！\n输出目录：{output_dir}\n是否打开输出目录？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            import os
            os.startfile(output_dir)

    def analysis_error(self, error_msg):
        """分析错误的回调函数"""
        self.run_btn.setEnabled(True)
        self.status_label.setText("分析失败")
        QMessageBox.critical(self, "错误", f"分析过程中出现错误：{error_msg}")