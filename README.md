# 智慧物流包裹质检与全链路监控系统

基于 Docker 容器云、深度学习与物联网技术的综合实践项目，包含传感器模拟、MQTT 消息传输、FastAPI 后端、MongoDB/Redis 存储、YOLO AI 推理、Vue/Nginx 网关和 Prometheus/Grafana 监控配置。

## 快速启动

在项目目录执行：

```bash
cd docker/logistics_project
docker compose up --build
```

启动后可访问：

- Web 监控大屏：<http://localhost>
- 后端 API 文档：<http://localhost/api/docs>
- Prometheus：<http://localhost:9090>
- Grafana：<http://localhost:3000>

## 目录结构

- `docker/logistics_project/`：可运行的微服务源码、Docker 配置、模型文件和监控配置。
- `materials/`：已匿名化的课程报告与演示文稿，Office 作者元数据也已清理。

## 数据集与运行数据

训练数据集、重复数据集压缩包和 MongoDB 本地数据库文件未提交到 GitHub：它们体积较大且属于运行产物。`docker/logistics_project/ai_engine/dataset/` 只保留数据集配置说明；需要训练时，可根据 `dataset-README.*.txt` 重新下载数据集。模型权重已保留在 `ai_engine/model/`，用于直接启动推理服务。

视频材料未上传；对应的课程报告和 PPT 已完成匿名化处理。
