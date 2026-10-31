from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import os
import json
import threading
import sys
import redis
from prometheus_client import start_http_server, Counter, Gauge, generate_latest

# 环境变量
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
DB_HOST = os.getenv("DB_HOST", "database")
DB_PORT = int(os.getenv("DB_PORT", 27017))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

app = FastAPI()

# 1. 连接 Redis (高可用缓存层)
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
    print("Connected to Redis")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    redis_client = None

# 2. 连接 MongoDB
try:
    mongo_client = MongoClient(DB_HOST, DB_PORT)
    db = mongo_client["logistics_db"]
    collection = db["sensor_readings"]
    print("Connected to MongoDB")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

# 3. Prometheus Metrics (DevOps 监控)
SENSOR_DATA_COUNT = Counter('sensor_data_received_total', 'Total sensor data received')
DAMAGE_DETECTED_COUNT = Counter('damage_detected_total', 'Total damage detected by AI')
CURRENT_TEMPERATURE = Gauge('current_temperature_celsius', 'Current Temperature')
MQTT_CONNECTED = Gauge('mqtt_connected_status', 'MQTT Connection Status')

# MQTT Client
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    MQTT_CONNECTED.set(1)
    client.subscribe("logistics/sensor/data")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        SENSOR_DATA_COUNT.inc() # 监控计数
        
        # 4. 滑动窗口滤波 & 多模态融合 (Data Fusion)
        # 简单模拟: 如果震动 > 0.8 (传感器) AND 温度 > 40 (环境), 标记为 HIGH_RISK
        # 真实项目中这里会结合 AI 的视觉结果 (payload 里可能包含 ai_result)
        vibration = payload.get("sensors", {}).get("vibration", 0)
        temp = payload.get("sensors", {}).get("temperature", 0)
        
        if vibration > 0.8:
            payload["fusion_risk"] = "HIGH"
            DAMAGE_DETECTED_COUNT.inc()
        else:
            payload["fusion_risk"] = "LOW"
            
        CURRENT_TEMPERATURE.set(temp)

        # 5. Redis 缓存 (削峰填谷)
        # 将最新数据写入 Redis list，模拟消息队列缓冲
        if redis_client:
            redis_client.lpush("sensor_buffer", json.dumps(payload))
            redis_client.ltrim("sensor_buffer", 0, 99) # 只保留最新100条

        # 6. 持久化存储
        collection.insert_one(payload)
        
    except Exception as e:
        print(f"Error processing message: {e}")

def start_mqtt():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Connection failed: {e}")
        MQTT_CONNECTED.set(0)

@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=start_mqtt)
    t.daemon = True
    t.start()

@app.get("/")
def read_root():
    return {"message": "Logistics Backend API 2.0 (Redis + Prometheus)"}

@app.get("/data")
def get_data(limit: int = 20):
    """优先从 Redis 读取 (体现缓存优势)，如果 Redis 挂了读 Mongo"""
    data = []
    if redis_client:
        try:
            # 从 Redis 获取最新的 limit 条
            items = redis_client.lrange("sensor_buffer", 0, limit - 1)
            data = [json.loads(i) for i in items]
        except:
            pass
    
    if not data:
        data = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
    
    return data

@app.get("/metrics")
def get_metrics():
    """Prometheus 拉取接口"""
    return generate_latest()

# 7. 反向控制接口 (Bidirectional Control)
@app.post("/control/stop")
def emergency_stop():
    """前端紧急停机按钮 -> 触发此接口 -> 发送 MQTT 指令 -> 模拟器停止"""
    try:
        mqtt_client.publish("logistics/control", json.dumps({"command": "STOP"}))
        return {"status": "success", "message": "Emergency Stop Command Sent!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/control/start")
def system_start():
    try:
        mqtt_client.publish("logistics/control", json.dumps({"command": "START"}))
        return {"status": "success", "message": "Start Command Sent!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
