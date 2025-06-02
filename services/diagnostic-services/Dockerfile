# 中医诊断服务 Docker 配置
# TCM Diagnosis Services Dockerfile

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # 图像处理依赖
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # 科学计算依赖
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    gfortran \
    # 传感器接口依赖
    libudev-dev \
    libusb-1.0-0-dev \
    # 蓝牙支持
    libbluetooth-dev \
    # 网络工具
    curl \
    wget \
    # 清理缓存
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY calculation-service/requirements.txt /app/calculation-requirements.txt
COPY palpation-service/requirements.txt /app/palpation-requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/calculation-requirements.txt && \
    pip install --no-cache-dir -r /app/palpation-requirements.txt

# 复制源代码
COPY calculation-service/ /app/calculation-service/
COPY palpation-service/ /app/palpation-service/
COPY config/ /app/config/
COPY tests/ /app/tests/

# 创建必要的目录
RUN mkdir -p /app/logs /app/data /app/temp

# 设置权限
RUN chmod +x /app/calculation-service/calculation_service/api/tcm_diagnosis_api.py
RUN chmod +x /app/palpation-service/palpation_service/api/sensor_management_api.py

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health && curl -f http://localhost:8001/health || exit 1

# 暴露端口
EXPOSE 8000 8001 8002

# 启动脚本
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"] 