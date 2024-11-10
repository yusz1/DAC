from pathlib import Path

class PathManager:
    def __init__(self, input_path):
        self.input_path = Path(input_path)
        
    @property
    def output_dir(self):
        return self.input_path.parent / "output"
        
    @property
    def distribution_dir(self):
        return self.output_dir / "distribution"
        
    def create_directories(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.distribution_dir.mkdir(parents=True, exist_ok=True)
        
    def print_paths(self):
        print("\n路径信息:")
        print(f"输入文件: {self.input_path}")
        print(f"输出目录: {self.output_dir}")
        print(f"分布图目录: {self.distribution_dir}\n") 