import time
import json
import random
import os
import requests
import paho.mqtt.client as mqtt

# 配置
BROKER = os.getenv("MQTT_BROKER", "mosquitto")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = "logistics/sensor/data"

def get_external_weather():
    """
    模拟获取外部真实天气数据 (互联互通)
    实际项目中可以替换为: http://api.openweathermap.org/data/2.5/weather?...
    这里为了保证演示稳定，连接一个稳定的公共 API，例如 httpbin 或公共天气接口
    """
    try:
        # 这里演示请求一个公共 IP 接口或时间接口来代表"联网能力"
        # 实际演示时，可以解释为正在校验当地环境参数
        resp = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC", timeout=2)
        if resp.status_code == 200:
            return {"connected": True, "source": "worldtimeapi.org"}
    except Exception as e:
        print(f"External API warning: {e}")
    return {"connected": False, "source": "local_fallback"}

# 全局运行状态
RUNNING = True

def on_message(client, userdata, msg):
    global RUNNING
    try:
        payload = json.loads(msg.payload.decode())
        command = payload.get("command")
        if command == "STOP":
            RUNNING = False
            print(">>> EMERGENCY STOP COMMAND RECEIVED! <<<")
        elif command == "START":
            RUNNING = True
            print(">>> SYSTEM START COMMAND RECEIVED! <<<")
    except:
        pass

def connect_mqtt():
    client = mqtt.Client()
    client.on_message = on_message # 绑定消息回调
    while True:
        try:
            client.connect(BROKER, PORT, 60)
            print("Connected to MQTT Broker!")
            client.subscribe("logistics/control") # 订阅控制指令 (反向控制回路)
            return client
        except Exception as e:
            print(f"Failed to connect, validation: {e}. Retrying in 5s...")
            time.sleep(5)

def run():
    client = connect_mqtt()
    client.loop_start()

    while True:
        if not RUNNING:
            time.sleep(1)
            continue
            
        # 1. 模拟传感器数据
        package_id = f"PKG-{random.randint(1000, 9999)}"
        weight = round(random.uniform(0.5, 20.0), 2)
        vibration = round(random.uniform(0, 1.0), 3) # 震动传感器

        # 2. 融合外部数据 (体现互联互通)
        ext_data = get_external_weather()
        
        # 模拟环境温湿度 (基于随机但在合理范围内波动)
        temp = round(random.uniform(20, 30), 1)
        humidity = round(random.uniform(40, 60), 1)

        payload = {
            "timestamp": time.time(),
            "package_id": package_id,
            "weight_kg": weight,
            "sensors": {
                "temperature": temp,
                "humidity": humidity,
                "vibration": vibration
            },
            "external_sync": ext_data, # 证明联网
            "status": "normal" if vibration < 0.8 else "warning"
        }

        # 3. 发送数据
        msg = json.dumps(payload)
        client.publish(TOPIC, msg)
        print(f"Published: {msg}")

        time.sleep(2) # 2秒发送一次

if __name__ == "__main__":
    run()
