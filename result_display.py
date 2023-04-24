import cv2
import numpy as np
import argparse
import os

def parse_line(line):
    elements = line.strip().split(' ')
    img_id = elements[0]
    image_path = elements[1]
    image_name = elements[1].split('/')[-1]
    bounding_boxes = []
    i = 2
    while i < len(elements):
        type_of_box = int(elements[i])
        confidence = float(elements[i+1])
        points = [float(e) for e in elements[i+2:i+10]]
        bounding_boxes.append((type_of_box, confidence, points))
        i += 10
    return img_id, image_path, image_name, bounding_boxes



def draw_bounding_boxes(image, bounding_boxes):
    color_box = (255, 165, 0) #橙色
    color_type_of_box = (165, 255, 0)  # 绿色
    color_confidence = (0, 0, 255)  # 红色

    for box in bounding_boxes:
        type_of_box, confidence, points = box
        pts = np.array(points, np.int32).reshape(-1, 2)
        cv2.polylines(image, [pts], True, color_box, 2)
        cv2.putText(image, f"{type_of_box}", (pts[0][0], pts[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_type_of_box, 2)
        cv2.putText(image, f"{confidence:.2f}", (pts[0][0] + 30, pts[0][1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_confidence, 2)


def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draw bounding boxes on images.")
    parser.add_argument('--save_path', type=str, help="Path to save the output images.", default=None)
    args = parser.parse_args()

    save_path = args.save_path
    if save_path:
        create_directory_if_not_exists(save_path)

    with open("result/result.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        img_id, image_path, image_name, bounding_boxes = parse_line(line)
        image = cv2.imread(image_path)
        draw_bounding_boxes(image, bounding_boxes)

        if save_path:
            output_path = f"{save_path}/{image_name}_r.jpg"
            cv2.imwrite(output_path, image)
        else:
            # 显示图像
            cv2.imshow(f"Image {img_id}", image)
            key = cv2.waitKey(0) & 0xFF
            cv2.destroyAllWindows()
            if key == ord('q'):
                print("程序已被用户终止。")
                break


