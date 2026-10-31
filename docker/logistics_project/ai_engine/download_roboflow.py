from roboflow import Roboflow
import os
import shutil

def download_yolo_dataset():
    # [UPDATED] 使用用户提供的新 Key 和项目路径
    api_key = "FCR7rfhYnuoWjqXFjCgs" 
    
    print(f"Initializing Roboflow with Key: {api_key}")
    rf = Roboflow(api_key=api_key)
    
    try:
        print("Downloading dataset in YOLOv8 format...")
        # 切换到用户的新工作空间和项目
        project = rf.workspace("new-workspace-1lgnq").project("damaged-package-detection-g2b6c")
        
        # [UPDATED] 下载为图像分类格式 (Classification)
        # 根据用户只做"破损/完好"分类的需求
        dataset = project.version(1).download("folder")
        
        print(f"Dataset downloaded to: {dataset.location}")
        
        # 移动/重命名到标准目录 'dataset'
        target_dir = "dataset"
        if os.path.exists(target_dir):
            # [FIX] 不能直接删除挂载点 (Errno 16)，而是清空里面的内容
            for filename in os.listdir(target_dir):
                file_path = os.path.join(target_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            
        # Roboflow 下载的文件在 dataset.location (通常是一个临时随机名目录)
        # 我们把里面的内容移动到 target_dir
        for item in os.listdir(dataset.location):
            s = os.path.join(dataset.location, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
        # 清理临时下载目录
        shutil.rmtree(dataset.location)
        
        print("\n[SUCCESS] YOLOv8 Dataset is ready in 'dataset/' folder!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Try providing a specific YOLOv8 download link if this fails.")

if __name__ == "__main__":
    download_yolo_dataset()
