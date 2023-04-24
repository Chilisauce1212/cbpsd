import os

# 获取 data/train/image 目录下的所有文件，并按照文件名排序
image_files = sorted(os.listdir('data/train/image'))

# 获取 data/train/label 目录下的所有文件，并按照文件名排序
label_files = sorted(os.listdir('data/train/label'))

# 重命名 image 和 label 文件名
for i in range(len(image_files)):
    os.rename('data/train/image/' + image_files[i], 'data/train/image/' + str(i) + '.jpg')
    os.rename('data/train/label/' + label_files[i], 'data/train/label/' + str(i) + '.txt')

# import cv2

# # 读取图像文件
# img = cv2.imread('data/train/image/9999.jpg')

# # 显示图像
# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
