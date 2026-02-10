# Frpc Web Configurator

这是一个使用 FastAPI 和 Vue.js 构建的 Web 应用，旨在提供一个图形化界面来配置 `frpc.toml` 文件，并最终作为一个 Docker 应用进行部署。

## ✨ 功能特性

*   **主页**: 以卡片形式展示已配置的 frp 代理，并提供一键快速访问功能。
*   **配置页**:
    *   以表格形式清晰地展示所有 frp 代理的详细配置。
    *   提供完整的 CRUD (创建、读取、更新、删除) 操作。
    *   可以为每个代理设置在主页的显示/隐藏状态。
    *   可以为每个代理设置一个易于识别的自定义显示名称。
*   **设置页**:
    *   可以自定义主页 "一键访问" 功能的目标 IP 地址。
*   **Docker 化**:
    *   提供 `Dockerfile`，使用多阶段构建，将前后端应用打包成一个轻量级的镜像。
    *   提供 `docker-compose.yml`，用于一键启动应用服务和 frpc 服务。

## 🚀 技术栈

*   **后端**: Python 3.11, FastAPI, Uvicorn
*   **前端**: Vue.js 3, Vite, TypeScript, Axios
*   **UI/CSS**: Pico.css
*   **容器化**: Docker, Docker Compose

## 🏃 如何运行

### 1. 准备工作

*   确保您的机器上已经安装了 [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
*   在项目根目录下，确保 `frpc.toml` 和 `app_config.json` 文件已存在。如果不存在，可以先手动创建。

### 2. 启动应用

在项目根目录下，执行以下命令：

```bash
docker-compose up --build
```

这将会：

1.  构建 `app` 服务的 Docker 镜像 (包括编译前端和安装后端依赖)。
2.  启动 `app` 服务和 `frpc` 服务。

### 3. 访问应用

*   **Web 界面**: 在您的浏览器中打开 `http://localhost:8000`。
*   **API**: API 服务也运行在 `http://localhost:8000`，您可以在 `/docs` 路径下查看由 FastAPI 自动生成的 API 文档 (即 `http://localhost:8000/docs`)。

## 📁 项目结构

```
.
├── backend/               # FastAPI 后端应用
│   ├── main.py            # API 逻辑
│   └── requirements.txt   # Python 依赖
├── frontend/              # Vue.js 前端应用
│   ├── src/
│   └── ...
├── app_config.json        # 应用配置文件 (目标 IP, 显示设置等)
├── frpc.toml              # frp 客户端配置文件
├── Dockerfile             # 用于构建应用镜像
└── docker-compose.yml     # Docker Compose 编排文件