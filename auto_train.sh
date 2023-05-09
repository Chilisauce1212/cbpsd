#!/bin/bash

# 删除已存在的 train.log 文件
rm -f train.log

# 创建一个临时文件以存储所有输出
temp_log="temp_train.log"

# 后台运行python脚本并将输出重定向到临时文件
nohup python train.py --data_path=data >$temp_log 2>&1 &

# 获取刚才启动的后台进程的PID
pid=$!

# 循环检查进程是否仍在运行
while kill -0 $pid 2>/dev/null; do
  # 仅保留临时文件的最后1000行并将其写入train.log
  tail -n 1000 $temp_log >train.log
  sleep 1
done

# 在进程完成后，仅保留最后1000行输出
tail -n 1000 $temp_log >train.log

# 删除临时文件
rm -f $temp_log
