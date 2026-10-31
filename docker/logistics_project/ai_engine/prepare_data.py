import os
import numpy as np
from PIL import Image, ImageDraw

# 配置目录
BASE_DIR = "dataset"
CLASSES = ["normal", "damaged"]
TRAIN_COUNT = 50
VAL_COUNT = 10

def create_dummy_image(path, label):
    """生成简单的模拟图片：正常(白色背景+蓝圈)，破损(白色背景+红叉)"""
    img = Image.new('RGB', (224, 224), color='white')
    draw = ImageDraw.Draw(img)
    
    if label == "normal":
        # 画一个蓝色的圆，代表完好
        draw.ellipse([50, 50, 174, 174], outline="blue", width=5)
    else:
        # 画一个红色的X，代表破损
        draw.line([50, 50, 174, 174], fill="red", width=5)
        draw.line([50, 174, 174, 50], fill="red", width=5)
    
    # 添加一些随机噪点
    pixels = img.load()
    for _ in range(500):
        x = np.random.randint(0, 224)
        y = np.random.randint(0, 224)
        pixels[x, y] = (0, 0, 0)

    img.save(path)

def make_dataset():
    if os.path.exists(BASE_DIR):
        print(f"Dataset directory '{BASE_DIR}' already exists. Skipping.")
        return

    for split in ["train", "validation"]:
        for cls in CLASSES:
            dir_path = os.path.join(BASE_DIR, split, cls)
            os.makedirs(dir_path, exist_ok=True)
            
            count = TRAIN_COUNT if split == "train" else VAL_COUNT
            print(f"Generating {count} images for {split}/{cls}...")
            
            for i in range(count):
                file_path = os.path.join(dir_path, f"{cls}_{i}.jpg")
                create_dummy_image(file_path, cls)
    
    print("Dummy dataset created successfully!")

if __name__ == "__main__":
    make_dataset()
