"""
# data_generator.py
数据表，
它的列包含SN,Time,Line,Camera_S这些基本信息，
以及20列数据，SN生成序列号，Camera_S是模组序列号，
20列数据符合正态分布，列名
S_NearSfr_Center1-S_NearSfr_Center4，
S_NearSfr_0.5-5-S_NearSfr_0.5-12，
S_NearSfr_0.8-13-S_NearSfr_0.8-20，
第一行和第二行是数据规格LSL和USL，
S_NearSfr_Center的规格是50-150，生成的数据范围是49-100；
S_NearSfr_0.5的规格是40-150，生成的数据范围是38-90；
S_NearSfr_0.8的规格是30-150，生成的数据范围是27-100，
数据有1%的空值
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataGenerator:
    def __init__(self, num_rows=500, seed=42):
        self.num_rows = num_rows
        np.random.seed(seed)
        
        # 定义数据规格和范围
        self.specs = {
            'Center': {'LSL': 50, 'USL': 150, 'range': (49, 100), 'mean': 75, 'std': 10},
            '0.5': {'LSL': 40, 'USL': 150, 'range': (38, 90), 'mean': 65, 'std': 10},
            '0.8': {'LSL': 30, 'USL': 150, 'range': (27, 100), 'mean': 65, 'std': 15}
        }
        
        # 定义列名
        self.columns = {
            'Center': [f'S_NearSfr_Center{i}' for i in range(1, 5)],
            '0.5': [f'S_NearSfr_0.5-{i}' for i in range(5, 13)],
            '0.8': [f'S_NearSfr_0.8-{i}' for i in range(13, 21)]
        }

    def generate_sn(self):
        """生成产品序列号: PXXYYYY (XX:月份, YYYY:序号)，部分SN重复1-3次"""
        base_date = datetime(2024, 1, 1)
        
        # 首先生成基础SN列表
        base_sn = [f"P{d.strftime('%m')}{i:04d}" 
                  for i, d in enumerate([base_date + timedelta(hours=x) 
                  for x in range(self.num_rows)])]
        
        # 随机选择一些SN进行重复
        repeat_count = int(self.num_rows * 0.05)  # 假设5%的SN会重复
        repeat_indices = np.random.choice(self.num_rows, size=repeat_count, replace=False)
        
        # 对选中的SN进行1-3次重复
        final_sn = base_sn.copy()
        for idx in repeat_indices:
            repeats = np.random.randint(1, 4)  # 1-3次重复
            for _ in range(repeats):
                insert_pos = np.random.randint(0, len(final_sn))
                final_sn.insert(insert_pos, base_sn[idx])
        
        # 确保总数量正确
        if len(final_sn) > self.num_rows:
            final_sn = final_sn[:self.num_rows]
        elif len(final_sn) < self.num_rows:
            final_sn.extend(base_sn[:(self.num_rows - len(final_sn))])
            
        return final_sn

    def generate_camera_s(self):
        """生成相机模组序列号: CAM24XXYYYY"""
        return [f"CAM24{np.random.randint(10, 13):02d}{i:04d}" 
                for i in range(self.num_rows)]

    def generate_normal_data(self, spec_type):
        """生成符合正态分布的数据"""
        spec = self.specs[spec_type]
        data = np.random.normal(
            loc=spec['mean'],
            scale=spec['std'],
            size=self.num_rows
        )
        data = np.clip(data, spec['range'][0], spec['range'][1])
        
        # 添加1%的空值
        nan_count = int(self.num_rows * 0.01)
        nan_indices = np.random.choice(self.num_rows, size=nan_count, replace=False)
        data[nan_indices] = np.nan
        return data

    def generate_dataset(self):
        """生成完整数据集"""
        # 基本信息列
        data = {
            "SN": self.generate_sn(),
            "Time": pd.date_range(start="2024-01-01", periods=self.num_rows, freq="h"),
            "Line": np.random.choice(["LineA", "LineB", "LineC"], size=self.num_rows),
            "Camera_S": self.generate_camera_s()
        }

        # 生成测量数据列
        for spec_type, cols in self.columns.items():
            for col in cols:
                data[col] = self.generate_normal_data(spec_type)

        return pd.DataFrame(data)

    def generate_specs_df(self):
        """生成规格数据框"""
        # 创建规格数据
        specs_data = {
            "SN": ["LSL", "USL"],  # 在SN列添加LSL和USL
            "Time": [np.nan, np.nan],
            "Line": [np.nan, np.nan],
            "Camera_S": [np.nan, np.nan]
        }
        
        # 添加测量数据的规格
        for spec_type, cols in self.columns.items():
            spec = self.specs[spec_type]
            for col in cols:
                specs_data[col] = [spec['LSL'], spec['USL']]
                
        return pd.DataFrame(specs_data)

    def save_to_excel(self, filename="data/input.xlsx"):
        """保存数据到Excel文件"""
        # 生成数据
        df = self.generate_dataset()
        specs_df = self.generate_specs_df()
        
        # 合并数据
        final_df = pd.concat([specs_df, df], ignore_index=True)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # 保存到Excel
        final_df.to_excel(filename, index=False)
        print(f"数据已保存到 {filename}")

def main():
    generator = DataGenerator(num_rows=500)
    generator.save_to_excel()

if __name__ == "__main__":
    main()
