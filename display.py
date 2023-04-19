import cv2
import numpy as np

def parse_line(line):
    elements = line.strip().split(' ')
    img_id = elements[0]
    image_path = elements[1]
    bounding_boxes = []
    i = 2
    while i < len(elements):
        type_of_box = int(elements[i])
        confidence = float(elements[i+1])
        points = [float(e) for e in elements[i+2:i+10]]
        bounding_boxes.append((type_of_box, confidence, points))
        i += 10
    return img_id, image_path, bounding_boxes



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


if __name__ == "__main__": 
    with open("result/result.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        img_id, image_path, bounding_boxes = parse_line(line)
        image = cv2.imread(image_path)
        draw_bounding_boxes(image, bounding_boxes)

        # 保存图像
        # output_path = f"output/{img_id}.jpg"
        # cv2.imwrite(output_path, image)

        # 显示图像
        cv2.imshow(f"Image {img_id}", image)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()
        if key == ord('q'):
            print("程序已被用户终止。")
            break


