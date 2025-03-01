# 使用更完整的基础镜像
FROM python:3.9-slim-bullseye

# 设置时区和清华镜像源
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖（补充更多OpenCV所需依赖）
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxt6 \
    dcm2niix \
    grep \          
    binutils \      
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 使用清华pip镜像
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY . .

EXPOSE 5000
CMD ["python", "app.py"]