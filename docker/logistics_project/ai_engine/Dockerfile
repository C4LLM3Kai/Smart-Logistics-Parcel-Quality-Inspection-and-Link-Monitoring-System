FROM python:3.9-slim

WORKDIR /app

# 1. 彻底替换 Debian 系统源为阿里云
# 直接复制本地配置好的源文件，避免 sed 命令在不同版本系统中的兼容性问题
COPY debian.sources /etc/apt/sources.list.d/debian.sources
# 删除旧的 lists 文件以确保更新生效，清除默认的 sources.list 以避免冲突
RUN rm -rf /etc/apt/sources.list.d/debian.list && \
    rm -f /etc/apt/sources.list


# 2. 安装 YOLO/OpenCV 所需的系统依赖
# 使用 --fix-missing 并增加重试机制
RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 3. 复制 Python 依赖清单
COPY requirements.txt .

# 4. 使用清华镜像源加速 pip 安装 (先升级 pip)
# 增加超时设置以应对大文件下载
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=100 -r requirements.txt

# 5. 复制项目剩余文件
COPY . .

# 6. 启动命令
CMD ["python", "inference.py"]