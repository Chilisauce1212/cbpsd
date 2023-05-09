#! /home/chili/miniconda3/envs/cbpsd/bin/python
import argparse
import os
import parking_context_recognizer.train as pcr_train
import parking_slot_detector.train as psd_train
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

os.environ['CUDA_VISIBLE_DEVICES'] = '1'
restore = 0
################
# ArgumentParser
#################
parser = argparse.ArgumentParser(description="context-based parking slot detector")

parser.add_argument("--data_path", type=str, default="/home/mind3/project/dataset/PIL-park/",
                    help="The path of the train tfrecord file.")

args = parser.parse_args()

# Train Parking Context Recognizer
# pcr_train.train(train_path=args.data_path)

if restore:
    restore_path = find_latest_checkpoint("weight_psd")
    restore_path0 = find_latest_checkpoint("weight_psd/type_0")
    restore_path1 = find_latest_checkpoint("weight_psd/type_1")
    restore_path2 = find_latest_checkpoint("weight_psd/type_2")
else:
    restore_path = "pre_weight/yolov3.ckpt"
    restore_path0 = find_latest_checkpoint("weight_psd")
    restore_path1 = find_latest_checkpoint("weight_psd")
    restore_path2 = find_latest_checkpoint("weight_psd")

# Train Parking Slot Detector
# trained_path = psd_train.train(args.data_path, restore_path, 'weight_psd')
psd_train.train(os.path.join(args.data_path, "t0"), restore_path0, 'weight_psd/type_0', fine_tune=True)
psd_train.train(os.path.join(args.data_path, "t1"), restore_path1, 'weight_psd/type_1', fine_tune=True)
psd_train.train(os.path.join(args.data_path, "t2"), restore_path2, 'weight_psd/type_2', fine_tune=True)

# # Train Parking Slot Detector
# psd_train.train(args.data_path, find_latest_checkpoint("weight_psd"), 'weight_psd')
# trained_path = psd_train.train(args.data_path, 'weight_psd/20230508_1646/model-epoch_10_step_26828_loss_7.3457_lr_1e-05', 'weight_psd')
# psd_train.train(os.path.join(args.data_path, "t0"), find_latest_checkpoint("weight_psd/type_0"), 'weight_psd/type_0', fine_tune=True)
# psd_train.train(os.path.join(args.data_path, "t1"), find_latest_checkpoint("weight_psd/type_1"), 'weight_psd/type_1', fine_tune=True)
# psd_train.train(os.path.join(args.data_path, "t2"), find_latest_checkpoint("weight_psd/type_2"), 'weight_psd/type_2', fine_tune=True)
