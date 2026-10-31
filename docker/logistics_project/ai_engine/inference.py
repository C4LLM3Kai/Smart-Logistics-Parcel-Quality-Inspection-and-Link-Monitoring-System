import os
import numpy as np
from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image

app = Flask(__name__)

# 加载模型
model = None
try:
    # YOLO 训练后的默认保存路径
    # 注意：train_yolo.py 中的 project="model", name="yolo_run"
    model_path = "./model/yolo_run/weights/best.pt"
    
    if os.path.exists(model_path):
        print(f"Loading custom YOLO model from {model_path}...")
        model = YOLO(model_path)
    else:
        print("Custom model not found, loading standard YOLOv8n for demo...")
        model = YOLO('yolov8n.pt') # 自动下载标准模型
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({"error": "Model not loaded"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    try:
        results = []
        if 'file' in request.files:
            file = request.files['file']
            img = Image.open(file.stream)
            
            # YOLO 推理 (Classification/Detection)
            # [FIX] 降低置信度阈值到 0.1 (10%)，防止刚训练的模型太保守
            # save=False 防止在服务器上生成太多临时图片
            yolo_results = model.predict(img, conf=0.1)
            
            # 解析结果
            for r in yolo_results:
                # 处理分类结果 (probs)
                if hasattr(r, 'probs') and r.probs is not None:
                    # 获取 Top-1 类别索引
                    cls_id = r.probs.top1
                    conf = float(r.probs.top1conf)
                    label = r.names[cls_id]
                    
                    # 总是返回结果，让前端展示具体识别到了什么
                    is_damaged = "damage" in label.lower()
                    
                    display_label = label
                    status = "RISK" if is_damaged else "SAFE"
                    
                    # 为了兼容前端逻辑，我们构造一个结果对象
                    # 如果是 RISK，我们给一个红框
                    # 如果是 SAFE，我们给一个绿框或者不给框 (这里给个全图框但前端可以根据 status 变色)
                    width, height = img.size
                    
                    results.append({
                        "label": display_label,
                        "score": conf,
                        "bbox": [0, 0, width, height],
                        "type": "classification",
                        "status": status, # [NEW] 显式状态
                        "is_damaged": is_damaged
                    })
                
                # 处理检测结果 (boxes) - 保留兼容性
                # 处理检测结果 (boxes) - 保留兼容性
                elif hasattr(r, 'boxes') and r.boxes is not None:
                     for box in r.boxes:
                        # 获取坐标 [x1, y1, x2, y2]
                        b = box.xyxy[0].tolist() 
                        # 转换为 [x, y, w, h] 以适配前端
                        x, y, x2, y2 = b[0], b[1], b[2], b[3]
                        w = x2 - x
                        h = y2 - y
                        
                        # 获取类别和置信度
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = model.names[cls_id]
                        
                        # [NEW] 细分破损类型映射 (Dataset 2 Labels)
                        # 'crushed', 'hole', 'scratched-cracked', 'shrunken-corner', 'tear-ripped'
                        label_map = {
                            "crushed": "挤压变形",
                            "hole": "破洞",
                            "scratched-cracked": "刮擦/裂痕",
                            "shrunken-corner": "护角凹陷",
                            "tear-ripped": "撕裂/破口",
                            "no defect": "完好"
                        }
                        
                        # 转换为中文展示，如果不在映射表中则保持原英文
                        display_label = label_map.get(label.lower(), label)
                        
                        # 判断是否为破损 (只要在我们的列表中就是破损)
                        damage_classes = ["crushed", "hole", "scratched-cracked", "shrunken-corner", "tear-ripped"]
                        is_damaged = label.lower() in damage_classes
                        
                        status = "RISK" if is_damaged else "SAFE"

                        results.append({
                            "label": display_label,
                            "original_label": label,
                            "score": conf,
                            "bbox": [x, y, w, h], 
                            "type": "object_detection",
                            "status": status,
                            "is_damaged": is_damaged
                        })
        
        # 如果没有识别出物体，返回空列表
        return jsonify({"success": True, "predictions": results})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ready", "model": "yolo"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
