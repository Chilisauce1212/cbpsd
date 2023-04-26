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
        x = max(0, min(int(calculated[0]), w - 1))
        y = max(0, min(int(calculated[1]), h - 1))
        new_bb.append(x)
        new_bb.append(y)
    return new_bb

def data_augment(jpg_file, txt_file, dst_jpg, dst_txt, rot_angle, flip=False, cover=False):
    image = cv2.imread(jpg_file)
    height, width, channel = image.shape

    
    matrix = cv2.getRotationMatrix2D((width / 2, height / 2), -rot_angle, 1)
    image_rot = cv2.warpAffine(image, matrix, (width, height), borderMode=cv2.BORDER_CONSTANT, borderValue=[128, 128, 128])

    type, angle, box_list = get_data_from_our_txt(txt_file, int, '\t')
    
    new_box_list = []

    if type != 3:
        for p in box_list:
            bb = [[int(p[1]), int(p[2])], [int(p[3]), int(p[4])], [int(p[5]), int(p[6])], [int(p[7]), int(p[8])]]
            new_bb = rotate_box(bb, _WIDTH/2, _HEIGHT/2, _HEIGHT, _WIDTH, -rot_angle)
            new_bb.insert(0, int(p[0]))
            new_box_list.append(new_bb)

    #遮盖处理
    if abs(angle) < 20 and type != 2 and cover and new_box_list:
        # 框的个数大于1时才遮盖最上框
        if len(new_box_list) > 1:
            # 寻找最上方的框
            top_box = min(new_box_list, key=lambda box: min(box[2], box[4], box[6], box[8]))

            # 计算遮罩区域的坐标
            sorted_y_coords_top = sorted([int(top_box[2]), int(top_box[4]), int(top_box[6]), int(top_box[8])])
            left_top_corner_y_top = sorted_y_coords_top[0]
            right_bottom_corner_y_top = sorted_y_coords_top[1]
            if right_bottom_corner_y_top - left_top_corner_y_top < 2:
                return
            # 生成一个随机遮盖比例，范围在 1/2 到 2/3 之间
            cover_ratio_top = random.uniform(1/2, 2/3)
            cover_y_top = int(right_bottom_corner_y_top - cover_ratio_top * (right_bottom_corner_y_top - left_top_corner_y_top))
            # 在图像上绘制遮罩
            cv2.rectangle(image_rot, (0, 0), (width, cover_y_top), (0, 0, 0), -1)

            # 计算遮罩后可见区域的四个角点
            new_top_box = [top_box[0]]
            box_top = top_box[1:]
            # 计算y=cover_y_top与第一和第二，第三和第四连线的交点
            for i in range(0, 8, 2):
                x1, y1 = box_top[i], box_top[i + 1] if box_top[i + 1] != cover_y_top else cover_y_top + 1
                x2, y2 = box_top[(i + 2) % 8], box_top[(i + 3) % 8] if box_top[(i + 3) % 8] != cover_y_top else cover_y_top + 1
                if (y1 > cover_y_top > y2) or (y2 > cover_y_top > y1):
                    intersect_x = x1 + (cover_y_top - y1) * (x2 - x1) / (y2 - y1)
                    new_top_box.extend([int(intersect_x), cover_y_top + 1])

                elif (y2 >= cover_y_top and y1 >= cover_y_top):
                    new_top_box.extend([x1, y1])
                    new_top_box.extend([x2, y2])

            #将最上方的框坐标更新
            new_box_list.remove(top_box)
            new_box_list.insert(0, new_top_box)

        # 寻找最下方的框
        bottom_box = max(new_box_list, key=lambda box: max(box[2], box[4], box[6], box[8]))

        # 计算遮罩区域的坐标
        sorted_y_coords = sorted([int(bottom_box[2]), int(bottom_box[4]), int(bottom_box[6]), int(bottom_box[8])])
        left_top_corner_y = sorted_y_coords[1]
        right_bottom_corner_y = sorted_y_coords[2]
        if right_bottom_corner_y - left_top_corner_y < 2:
            return 
        # 生成一个随机遮盖比例，范围在 1/2 到 2/3 之间
        cover_ratio = random.uniform(1/2, 2/3)
        cover_y = int(left_top_corner_y + cover_ratio * (right_bottom_corner_y - left_top_corner_y))
        # 在图像上绘制遮罩
        cv2.rectangle(image_rot, (0, cover_y), (width, height), (0, 0, 0), -1)
        # print(jpg_file)
        # print(new_box_list)
        # 计算遮罩后可见区域的四个角点
        new_bottom_box = [bottom_box[0]]
        box = bottom_box[1:]
        # 计算y=cover_y与第一和第二，第三和第四连线的交点
        for i in range(0, 8, 2):
            x1, y1 = box[i], box[i + 1] if box[i + 1] != cover_y else cover_y - 1
            x2, y2 = box[(i + 2) % 8], box[(i + 3) % 8] if box[(i + 3) % 8] != cover_y else cover_y - 1
            if (y1 < cover_y < y2) or (y2 < cover_y < y1):
                intersect_x = x1 + (cover_y - y1) * (x2 - x1) / (y2 - y1)
                new_bottom_box.extend([int(intersect_x), cover_y -1])
                # print(f"1 {x1}-{y1} {x2} {y2} -> {int(intersect_x)} {cover_y -1}")
            elif (y2 <= cover_y and y1 <= cover_y):
                new_bottom_box.extend([x1, y1])
                new_bottom_box.extend([x2, y2])
                # print(f"2 {x1}-{y1} {x2} {y2} -> {x1}-{y1} {x2} {y2}")


        
        #将最下方的框坐标更新
        new_box_list.remove(bottom_box)
        new_box_list.append(new_bottom_box)
        # print(f"cover_y:{cover_y}")
        # print(new_box_list)
        # print()

    #翻转处理
    if flip:
        image_rot = cv2.flip(image_rot, 0)

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

    
    flip_box_list = []
    if type != 3 and flip:
        for p in new_box_list:
            bb = [int(p[3]), height -1 - int(p[4]), int(p[1]), height - 1 - int(p[2]), int(p[7]), height-1 - int(p[8]), int(p[5]), height-1 - int(p[6])]
            bb.insert(0, int(p[0]))
            flip_box_list.insert(0, bb)
        new_box_list = flip_box_list
    # print(new_box_list)
    write_data_to_our_txt(dst_txt, type, new_angle, new_box_list)
    cv2.imwrite(dst_jpg, image_rot)
    
def run_single(data_path):
    image_path = os.path.join(data_path, "image")
    label_path = os.path.join(data_path, "label")
    jpg_files = sorted(os.listdir(image_path))
    txt_files = sorted(os.listdir(label_path))

    #单线程处理
    for jpg_file, txt_file in zip(jpg_files, txt_files):
            src_image_file = os.path.join(image_path, jpg_file)
            src_label_file = os.path.join(label_path, txt_file)
            print(jpg_file)
            for angle in range(-5, 6, 5):
                for flip in [True, False]:
                    for cover in [True, False]:
                        if angle == 0 and flip == False and cover == False:
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
                        data_augment(src_image_file, src_label_file,dst_image_file,dst_label_file,angle,flip,cover)

def run_multiple(data_path,thread_num):
    image_path = os.path.join(data_path, "image")
    label_path = os.path.join(data_path, "label")
    jpg_files = sorted(os.listdir(image_path))
    txt_files = sorted(os.listdir(label_path))                        
    #多线程处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_num) as executor:
        futures = []
        for jpg_file, txt_file in zip(jpg_files, txt_files):
            src_image_file = os.path.join(image_path, jpg_file)
            src_label_file = os.path.join(label_path, txt_file)
            print(jpg_file)
            for angle in range(-5, 6,5):
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

def run(data_path):
    run_multiple(data_path, thread_num=12)
    # run_single(data_path)