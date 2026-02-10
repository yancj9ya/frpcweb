# Frpc Web Configurator

这是一个基于 Flask 的轻量级 Web 应用，用于图形化管理 `frpc.toml` 与 `app_config.json`，并支持容器化部署。

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
    *   提供 `Dockerfile` 构建镜像。
    *   提供 `docker-compose.yml`，用于一键启动应用服务和 frpc 服务。

## 🚀 技术栈

*   **后端**: Python 3.11, Flask
*   **前端**: Jinja 模板 + 原生 HTML/CSS/JS
*   **UI/CSS**: 自定义样式
*   **容器化**: Docker, Docker Compose

## 🏃 如何运行

### 1. 准备工作

*   确保您的机器上已经安装了 [Docker](https://www.docker.com/) 和 [Docker Compose](https://docs.docker.com/compose/install/)。
*   在项目根目录下，确保 `frpc.toml` 和 `app_config.json` 文件已存在。如果不存在，可以先手动创建。

### 2. 启动应用（Docker Compose）

在项目根目录下，执行以下命令：

```bash
docker-compose up --build
```

这将会：

1.  构建 `app` 服务的 Docker 镜像。
2.  启动 `app` 服务和 `frpc` 服务。

### 3. 访问应用

*   **Web 界面**: 在您的浏览器中打开 `http://localhost:8000`。
*   **Web 界面**: 打开后即可管理代理配置和快速访问。

## 📦 Docker 镜像

已配置 GitHub Actions 自动构建并推送到 GHCR 与 Docker Hub。

拉取镜像示例：

```bash
docker pull ghcr.io/yancj9ya/frpcweb:latest
docker pull docker.io/yancjycj/frpcweb:latest
```

使用镜像运行示例（请按需挂载配置文件）：

```bash
docker run --rm -p 8000:8000 ^
  -v %cd%/frpc.toml:/app/frpc.toml ^
  -v %cd%/app_config.json:/app/app_config.json ^
  ghcr.io/yancj9ya/frpcweb:latest
```

发布版本号：

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 📁 项目结构

```
.
├── app/                   # Flask 应用
│   ├── templates/         # Jinja 模板
│   └── static/            # 静态资源
├── app_config.json        # 应用配置文件 (目标 IP, 显示设置等)
├── frpc.toml              # frp 客户端配置文件
├── main.py                # 应用入口
├── requirements.txt       # Python 依赖
├── Dockerfile             # 用于构建应用镜像
└── docker-compose.yml     # Docker Compose 编排文件
