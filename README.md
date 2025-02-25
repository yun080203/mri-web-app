backend/：

后端代码，使用 Python（Flask）实现图像处理逻辑。

frontend/：

前端代码，使用 React 实现用户界面。

public/：存放静态文件（如 index.html）。

node_modules/：存放 Node.js 依赖包（无需手动修改）。

package.json：定义项目依赖和脚本。

package-lock.json：锁定依赖版本（无需手动修改）。

src/：存放 React 源码。

docker-compose.yml：

定义 Docker 容器配置，用于启动前后端服务。

.gitignore：

定义 Git 忽略的文件和目录。

README.md：

项目说明文档。

# Brain MRI Image Processing Web App

## 项目简介
本项目是一个用于处理脑部 MRI 图像的网页应用，支持图像上传、去噪、增强对比度、分割病变区域等功能。

## 安装步骤
1. 克隆项目：
   ```bash
   git clone https://github.com/your-repo/mri-web-app.git
2.项目启动
   docker-compose up --build

使用说明
访问 http://localhost:3000。

上传脑部 MRI 图像。

查看处理后的图像和报告

