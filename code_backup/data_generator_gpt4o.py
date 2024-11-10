import os
import pandas as pd
import numpy as np

# 设置随机种子以确保结果可重复
np.random.seed(42)

# 定义数据规格
num_rows = 500  # 数据行数

# 生成基本信息列
sn = [f"SN{1000 + i:04d}" for i in range(num_rows)]  # SN序列号，格式为SN1000, SN1001, ...
time = pd.date_range(start="2023-01-01", periods=num_rows, freq="h")
line = np.random.choice(["Line1", "Line2", "Line3"], size=num_rows)
camera_s = [f"Cam{chr(65 + i % 26)}{i:03d}" for i in range(num_rows)]  # Camera_S序列号，格式为CamA000, CamB001, ...

# 生成符合正态分布的20列数据
def generate_data(mean, std, size, lower_bound, upper_bound):
    data = np.random.normal(loc=mean, scale=std, size=size)
    data = np.clip(data, lower_bound, upper_bound)
    # Introduce 1% NaN values
    nan_indices = np.random.choice(size, size=int(size * 0.01), replace=False)
    data[nan_indices] = np.nan
    return data

# 生成数据列
data_columns = {
    "S_NearSfr_Center1": generate_data(75, 10, num_rows, 49, 100),
    "S_NearSfr_Center2": generate_data(75, 10, num_rows, 49, 100),
    "S_NearSfr_Center3": generate_data(75, 10, num_rows, 49, 100),
    "S_NearSfr_Center4": generate_data(75, 10, num_rows, 49, 100),
    "S_NearSfr_0.5-5": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.5-6": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.5-7": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.5-8": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.5-9": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.5-10": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.5-11": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.5-12": generate_data(65, 10, num_rows, 38, 90),
    "S_NearSfr_0.8-13": generate_data(65, 15, num_rows, 27, 100),
    "S_NearSfr_0.8-14": generate_data(65, 15, num_rows, 27, 100),
    "S_NearSfr_0.8-15": generate_data(65, 15, num_rows, 27, 100),
    "S_NearSfr_0.8-16": generate_data(65, 15, num_rows, 27, 100),
    "S_NearSfr_0.8-17": generate_data(65, 15, num_rows, 27, 100),
    "S_NearSfr_0.8-18": generate_data(65, 15, num_rows, 27, 100),
    "S_NearSfr_0.8-19": generate_data(65, 15, num_rows, 27, 100),
    "S_NearSfr_0.8-20": generate_data(65, 15, num_rows, 27, 100),
}

# 创建DataFrame
df = pd.DataFrame({
    "SN": sn,
    "Time": time,
    "Line": line,
    "Camera_S": camera_s,
    **data_columns
})

# 添加规格行
specs = {
    "S_NearSfr_Center1": [50, 150],
    "S_NearSfr_Center2": [50, 150],
    "S_NearSfr_Center3": [50, 150],
    "S_NearSfr_Center4": [50, 150],
    "S_NearSfr_0.5-5": [40, 150],
    "S_NearSfr_0.5-6": [40, 150],
    "S_NearSfr_0.5-7": [40, 150],
    "S_NearSfr_0.5-8": [40, 150],
    "S_NearSfr_0.5-9": [40, 150],
    "S_NearSfr_0.5-10": [40, 150],
    "S_NearSfr_0.5-11": [40, 150],
    "S_NearSfr_0.5-12": [40, 150],
    "S_NearSfr_0.8-13": [30, 150],
    "S_NearSfr_0.8-14": [30, 150],
    "S_NearSfr_0.8-15": [30, 150],
    "S_NearSfr_0.8-16": [30, 150],
    "S_NearSfr_0.8-17": [30, 150],
    "S_NearSfr_0.8-18": [30, 150],
    "S_NearSfr_0.8-19": [30, 150],
    "S_NearSfr_0.8-20": [30, 150],
}

# 将规格行插入到DataFrame的顶部
spec_df = pd.DataFrame(specs, index=["LSL", "USL"])
spec_df = spec_df.reindex(columns=df.columns, fill_value=np.nan)
df = pd.concat([spec_df, df], ignore_index=True)

# 确保目录存在
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# 保存到Excel
df.to_excel(os.path.join(output_dir, "input.xlsx"), index=False)