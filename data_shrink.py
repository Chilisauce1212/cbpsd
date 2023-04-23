import os

def remove_files_with_underscore(folder):
    for filename in os.listdir(folder):
        if "_" in filename:
            file_path = os.path.join(folder, filename)
            os.remove(file_path)

def main():
    image_folder = "data/train/image"
    label_folder = "data/train/label"

    remove_files_with_underscore(image_folder)
    remove_files_with_underscore(label_folder)

if __name__ == "__main__":
    main()
