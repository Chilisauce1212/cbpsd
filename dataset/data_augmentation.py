import numpy as np
import cv2
import os
from dataset.dataset_utils import *
import concurrent.futures
import random
import traceback

_WIDTH = 256
_HEIGHT = 768

def line_intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    denominator = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))
    if denominator == 0:
        return None
    px = (((x1 * y2) - (y1 * x2)) * (x3 - x4) - (x1 - x2) * ((x3 * y4) - (y3 * x4))) / denominator
    py = (((x1 * y2) - (y1 * x2)) * (y3 - y4) - (y1 - y2) * ((x3 * y4) - (y3 * x4))) / denominator
    return int(px), int(py)


def rotate_box(bb, cx, cy, h, w, rot_angle):
    # new_bb = list(bb)
    new_bb = []
    for i,coord in enumerate(bb):
        # opencv calculates standard transformation matrix
        M = cv2.getRotationMatrix2D((cx, cy), rot_angle, 1.0)
        # compute the new bounding dimensions of the image
        M[0, 2] += (w / 2) - cx
        M[1, 2] += (h / 2) - cy
        # Prepare the vector to be transformed
        v = [coord[0],coord[1],1]
        # Perform the actual rotation and return the image
        calculated = np.dot(M,v)
        new_bb.append(int(calculated[0]))
        new_bb.append(int(calculated[1]))
    return new_bb

def data_augment(jpg_file, txt_file, dst_jpg, dst_txt, rot_angle, flip=False, cover=False):
    image = cv2.imread(jpg_file)
    height, width, channel = image.shape

    if flip:
        image = cv2.flip(image, 0)

    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), -rot_angle, 1)
    image_rot = cv2.warpAffine(image, matrix, (width, height), borderMode=cv2.BORDER_CONSTANT, borderValue=[128, 128, 128])

    type, angle, box_list = get_data_from_our_txt(txt_file, int, '\t')
    if type == 3:
        new_angle = 0
    else:
        if flip:
            new_angle = -angle + rot_angle
        else:
            new_angle = angle + rot_angle
    if new_angle < -180:
        new_angle += 360
    elif new_angle > 180:
        new_angle -= 360
    new_box_list = []

    for p in box_list:
        if flip:
            bb = [[int(p[3]), height -1 - int(p[4])], [int(p[1]), height - 1 - int(p[2])], [int(p[7]), height-1 - int(p[8])], [int(p[5]), height-1 - int(p[6])]]
        else:
            bb = [[int(p[1]), int(p[2])], [int(p[3]), int(p[4])], [int(p[5]), int(p[6])], [int(p[7]), int(p[8])]]
        new_bb = rotate_box(bb, _WIDTH/2, _HEIGHT/2, _HEIGHT, _WIDTH, -rot_angle)
        new_bb.insert(0, int(p[0]))
        if flip:
            new_box_list.insert(0, new_bb)
        else:
            new_box_list.append(new_bb)

    if cover and new_box_list:
        # 寻找最下方的框
        bottom_box_index = max(range(len(new_box_list)), key=lambda i: max(new_box_list[i][1::2]))
        bottom_box = new_box_list[bottom_box_index]

        # 计算遮罩区域的坐标
        left_top_corner_y = max(int(bottom_box[2]), int(bottom_box[8]))
        right_bottom_corner_y = min(int(bottom_box[4]), int(bottom_box[6]))
        # 生成一个随机遮盖比例，范围在 1/3 到 2/3 之间
        cover_ratio = random.uniform(1/3, 2/3)
        cover_y = int(left_top_corner_y + cover_ratio * (right_bottom_corner_y - left_top_corner_y))
        # 在图像上绘制遮罩
        cv2.rectangle(image_rot, (0, cover_y), (width, height), (0, 0, 0), -1)

        # 计算遮罩后可见区域的四个角点
        new_bottom_box = [bottom_box[0]]
        new_bottom_box.extend([bottom_box[1], bottom_box[2]])
        # 计算y=cover_y与第一和第二，第三和第四连线的交点
        for i in range(1, 7, 4):
            x1, y1 = bottom_box[i], bottom_box[i+1]
            x2, y2 = bottom_box[i+2], bottom_box[i+3]
            
            intersect_x = x1 + (cover_y - y1) * (x2 - x1) / (y2 - y1)
            new_bottom_box.extend([int(intersect_x), cover_y - 1])
        
        new_bottom_box.extend([bottom_box[7], bottom_box[8]])
        #将最下方的框坐标更新
        new_box_list.remove(bottom_box)
        new_box_list.append(new_bottom_box)
    write_data_to_our_txt(dst_txt, type, new_angle, new_box_list)
    cv2.imwrite(dst_jpg, image_rot)

def run(data_path):
    image_path = os.path.join(data_path, "image")
    label_path = os.path.join(data_path, "label")
    jpg_files = sorted(os.listdir(image_path))
    txt_files = sorted(os.listdir(label_path))

    #单线程处理
    # for jpg_file, txt_file in zip(jpg_files, txt_files):
    #         src_image_file = os.path.join(image_path, jpg_file)
    #         src_label_file = os.path.join(label_path, txt_file)
    #         print(jpg_file)
    #         for angle in range(-5, 6):
    #             for flip in [True, False]:
    #                 for cover in [True, False]:
    #                     if angle == 0 and flip == False and cover == False:
    #                         continue                
    #                     file_suffix = ""
    #                     if flip:
    #                         file_suffix += "_flip"
    #                     if cover:
    #                         file_suffix += "_cover"

    #                     dst_jpg_file = jpg_file.replace(".jpg", "{}_{}.jpg".format(file_suffix, angle))
    #                     dst_txt_file = txt_file.replace(".txt", "{}_{}.txt".format(file_suffix, angle))
    #                     dst_image_file = os.path.join(image_path, dst_jpg_file)
    #                     dst_label_file = os.path.join(label_path, dst_txt_file)
    #                     try:
    #                         data_augment(src_image_file, src_label_file,dst_image_file,dst_label_file,angle,flip,cover)
    #                     except Exception as e:
    #                         tb = traceback.format_exc()
    #                         print(f"任务执行过程中发生异常: {e}\n{tb}")
                        
    #多线程处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = []
        for jpg_file, txt_file in zip(jpg_files, txt_files):
            src_image_file = os.path.join(image_path, jpg_file)
            src_label_file = os.path.join(label_path, txt_file)
            print(jpg_file)
            for angle in range(-5, 6):
                for flip in [True, False]:
                    for cover in [True, False]:
                        if angle == 0 and flip == False:
                            continue                
                        file_suffix = ""
                        if flip:
                            file_suffix += "_flip"
                        if cover:
                            file_suffix += "_cover"

                        dst_jpg_file = jpg_file.replace(".jpg", "{}_{}.jpg".format(file_suffix, angle))
                        dst_txt_file = txt_file.replace(".txt", "{}_{}.txt".format(file_suffix, angle))
                        dst_image_file = os.path.join(image_path, dst_jpg_file)
                        dst_label_file = os.path.join(label_path, dst_txt_file)

                        # 提交任务到线程池
                        future = executor.submit(data_augment, src_image_file, src_label_file, dst_image_file, dst_label_file, angle, flip, cover)
                        futures.append(future)

        # 等待所有任务完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                tb = traceback.format_exc()
                print(f"任务执行过程中发生异常: {e}\n{tb}")
