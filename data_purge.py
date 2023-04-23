import os

# 设置目录路径
image_dir = 'data/train/image'
label_dir = 'data/train/label'

# 获取文件列表并排序
image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
label_files = sorted([f for f in os.listdir(label_dir) if f.endswith('.txt')])

# 获取前100个jpg文件的文件名（不包括扩展名）
top_100_images = [os.path.splitext(f)[0] for f in image_files[:100]]

# 删除不在top_100_images列表中的txt文件
for label_file in label_files:
    file_name, _ = os.path.splitext(label_file)
    if file_name not in top_100_images:
        os.remove(os.path.join(label_dir, label_file))

# 删除前100个jpg文件之外的jpg文件
for image_file in image_files[100:]:
    os.remove(os.path.join(image_dir, image_file))
