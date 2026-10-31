from ultralytics import YOLO
import os

def train_yolo():
    print("Initializing YOLOv8 Object Detection model...")
    # [FIX] 切换回目标检测模型 (Object Detection)
    model = YOLO('yolov8n.pt') 

    print("Starting training...")
    # [FIX] 检测任务必须指向 data.yaml
    # GitHub Action / Docker 挂载通常是 /app/dataset
    yaml_path = os.path.abspath("dataset/data.yaml")
    
    if not os.path.exists(yaml_path):
        print(f"Error: {yaml_path} not found. Please unzip dataset into 'ai_engine/dataset' folder.")
        return

    print(f"Using configuration: {yaml_path}")

    # 训练
    results = model.train(
        data=yaml_path,
        epochs=50,
        imgsz=640, # 检测任务通常用 640x640
        project="model",
        name="yolo_run",
        exist_ok=True
    )
    
    # 导出模型为最佳实践格式
    success = model.export(format='saved_model') 
    
    # 也可以直接保留 best.pt
    print("Training finished! Best model is at 'model/yolo_run/weights/best.pt'")

if __name__ == "__main__":
    train_yolo()
