import os
from pathlib import Path
import re

def find_latest_checkpoint(directory):
    type_2_dir = Path(directory)
    
    # 获取所有子文件夹
    subdirs = [d for d in type_2_dir.iterdir() if d.is_dir()]

    # 按日期排序子文件夹
    subdirs = sorted(subdirs, key=lambda x: x.name, reverse=True)

    # 初始化最大step和对应的checkpoint文件名
    max_step = 0
    max_step_checkpoint = None

    # 遍历子文件夹
    for subdir in subdirs:
        for file in subdir.iterdir():
            # 匹配checkpoint文件
            match = re.match(r'model-epoch_\d+?_step_(\d+?)_.*\.meta', file.name)
            if match:
                step = int(match.group(1))
                if step > max_step:
                    max_step = step
                    max_step_checkpoint = file.with_suffix('')

    if max_step_checkpoint:
        return str(max_step_checkpoint)
    else:
        return "No checkpoint file found."

directory = "weight_psd"
result = find_latest_checkpoint(directory)
print(result)
