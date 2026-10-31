# 智慧物流包裹质检与全链路监控系统

基于 Docker 容器云、深度学习与物联网技术的综合实践项目。

## 1. 项目架构 (7 容器微服务)

| 容器服务 | 名称 | 作用 | 端口映射 |
| :--- | :--- | :--- | :--- |
| **Nginx** | `nginx` | **统一网关入口**，反向代理前端与后端 | 80:80 |
| **Frontend** | `frontend` | Vue 3 可视化大屏，展示实时数据 | (内部 80) |
| **Backend** | `backend` | FastAPI 后端，处理业务逻辑与存储 | (内部 8000) |
| **Mosquitto** | `mosquitto` | MQTT 消息代理，设备通讯核心 | 1883, 9001 |
| **Simulator** | `simulator` | **Python 模拟器**，生成数据并调用外部天气 API (互联互通) | - |
| **AI Engine** | `ai_engine` | TensorFlow 深度学习推理服务 (MobileNetV2) | (内部 5000) |
| **Database** | `database` | MongoDB 数据库，持久化存储传感器日志 | 27017 |

## 2. 快速启动

在 `logistics_project` 目录下执行：

```bash
docker-compose up --build
```

启动后访问：
*   **Web 监控大屏**: [http://localhost](http://localhost)
*   **后端 API 文档**: [http://localhost/api/docs](http://localhost/api/docs)
*   **MongoDB**: `localhost:27017`

## 3. 功能亮点

1.  **复杂工程架构**: 采用 Nginx 网关模式，前后端分离，模拟真实生产部署。
2.  **互联互通**: Simulator 容器实时请求外部 API (WorldTime/Weather) 混入数据。
3.  **AI 赋能**: 独立的 AI 容器运行 MobileNetV2 模型进行图片分类。
4.  **数据流完整**: Simulator -> MQTT -> Backend -> MongoDB -> API -> Frontend。
