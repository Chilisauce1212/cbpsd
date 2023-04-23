import os
import cv2
import numpy as np
# 设置目录路径
image_dir = 'data/train/image'
label_dir = 'data/train/label'

# 获取文件列表并排序
image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
label_files = sorted([f for f in os.listdir(label_dir) if f.endswith('.txt')])

def draw_boxes(image, boxes):
    for box in boxes:
        car_type, x1, y1, x2, y2, x3, y3, x4, y4 = [int(x) for x in box[:-1]]
        pts = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 255), 2)

def read_labels(label_path):
    with open(label_path, 'r') as f:
        content = f.readlines()
    return [line.split('\t') for line in content[2:]]

for image_file, label_file in zip(image_files, label_files):
    image_path = os.path.join(image_dir, image_file)
    label_path = os.path.join(label_dir, label_file)

    # 读取图像和标签
    image = cv2.imread(image_path)
    labels = read_labels(label_path)
    # print(labels)
    # print(f"file : {image_path}")
    # print()
    # 画框
    draw_boxes(image, labels)

    # 显示图像
    cv2.imshow('Image with Boxes', image)

    # 按空格键读取下一个，按'q'键退出
    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
