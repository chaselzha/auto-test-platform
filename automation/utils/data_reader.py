# automation/utils/data_reader.py
import os
import yaml
from pathlib import Path


def load_yaml(file_path):
    """
    加载 YAML 文件

    Args:
        file_path: 相对于 automation 目录的路径

    Returns:
        解析后的数据
    """
    # 获取 automation 目录
    current_dir = Path(__file__).parent.parent  # automation/
    full_path = current_dir / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"数据文件不存在: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)