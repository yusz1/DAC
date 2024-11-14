def update_config(config, ui):
    """根据UI设置更新配置"""
    # 更新文件路径
    if ui.file_path.text():
        config.DATA['path'] = ui.file_path.text()
    
    # 更新图表类型配置
    config.PLOT.update({
        'show_lsl': ui.show_lsl_check.isChecked(),
        'show_usl': ui.show_usl_check.isChecked(),
        'title_prefix': ui.title_prefix_input.text(),
        'enable_distribution': ui.dist_check.isChecked(),
        'enable_boxplot': ui.box_check.isChecked(),
        'enable_group_boxplot': ui.group_box_check.isChecked(),
        'enable_all_columns_compare': ui.all_compare_check.isChecked(),
        'enable_correlation': ui.corr_check.isChecked()
    })
    
    # 更新数据处理配置
    config.DATA_PROCESSING.update({
        'remove_duplicates': ui.remove_dup_check.isChecked(),
        'remove_null': ui.remove_null_check.isChecked(),
        'remove_invalid': ui.remove_invalid_check.isChecked()
    })
    
    # 更新分组分析配置
    config.DATA_PROCESSING['group_analysis'].update({
        'enabled': ui.group_enabled_check.isChecked(),
        'group_by': ui.group_by_input.text() if ui.group_by_input.text() else 'Line'
    })
    
    return config 