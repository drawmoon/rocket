- [Docker Compose](#docker-compose)
  - [简介](#简介)
  - [安装](#安装)
  - [Composefile](#composefile)
    - [拉取镜像运行服务](#拉取镜像运行服务)
    - [构建镜像运行服务](#构建镜像运行服务)
    - [指定镜像名称](#指定镜像名称)
    - [指定 Composefile](#指定-composefile)
  - [命令](#命令)
    - [启动项目](#启动项目)
    - [停止项目](#停止项目)
    - [列出项目所有的服务](#列出项目所有的服务)
    - [查看服务的日志](#查看服务的日志)
    - [进入到服务中](#进入到服务中)
    - [启动服务](#启动服务)
    - [重新启动服务](#重新启动服务)
    - [停止正在运行的服务](#停止正在运行的服务)
    - [暂停服务](#暂停服务)
    - [恢复服务](#恢复服务)
    - [删除服务](#删除服务)
    - [构建项目](#构建项目)
  - [卷（Volume）](#卷volume)
    - [具体路径 (Bind Mount)](#具名卷-named-volume)
    - [具名卷 (Named Volume)](#具名卷-named-volume)
  - [网络](#网络)
    - [使用主机网络](#使用主机网络)

## 简介

Docker Compose 是 Docker 官方的多容器应用编排工具，用于通过一个配置文件定义和管理多个容器服务，配置文件通常被命名为 `docker-compose.yml`。

## 安装

```bash
sudo apt update
sudo apt install docker-compose-plugin
```

检查 Docker Compose 是否成功安装

```bash
docker compose version
```

> 该安装方式需要系统中已经安装好了 Docker，`docker compose` 命令是 Docker Compose v2 版本，是 Docker 官方推荐的版本，它作为 Docker CLI 插件集成在 `docker` 命令中，而不是独立的 docker compose 二进制程序。

## Composefile

### 拉取镜像运行服务

编写 `docker-compose.yml` 文件：

```yaml
version: "3"
services: 

  nginx:
    image: nginx
    ports:
      - "80:80"
    restart: always
```

运行 DockerCompose 项目：

```bash
docker compose up
```

### 构建镜像运行服务

编写 `Dockerfile` 文件：

```docker
FROM node:14.18.1 AS build
WORKDIR /source
COPY . .
RUN yarn install \
    && npm run build

FROM node:14.18.1-alpine
WORKDIR /app
COPY --from=build /source/dist .
COPY --from=build /source/node_modules node_modules
ENTRYPOINT [ "node", "main" ]
```

编写 `docker-compose.yml` 文件：

```yaml
version: "3"
services: 

  app:
    build: .
    ports:
      - "3000:3000"
    restart: always
```

运行 DockerCompose 项目：

```bash
docker compose up --build
```

### 指定镜像名称

```yaml
version: "3"
services: 

  app:
    build: .
    image: myapp:stable
    ports:
      - "3000:3000"
    restart: always
```

### 指定 Composefile

```yaml
version: "3"
services: 

  app:
    build:
      context: .
      dockerfile: Default_Dockerfile
    ports:
      - "3000:3000"
    restart: always
```

## 命令

### 启动项目

自动构建镜像、创建网络、创建并启动服务：

```bash
docker compose up
```

后台运行：

```bash
docker compose up -d
```

指定 DockerCompose 配置文件：

```bash
docker compose -f docker-compose.production.yml up
```

指定服务：

```bash
docker compose up nginx
```

重新构建：

```bash
docker compose up --build
```

### 停止项目

停止并删除网络、服务。

```bash
docker compose down
```

### 列出项目所有的服务

```bash
docker compose ps
```

### 查看服务的日志

```bash
docker compose logs nginx
```

`-f` 监听服务的输出

```bash
docker compose logs nginx -f
```

### 进入到服务中

```bash
docker compose exec nginx bash
```

### 启动服务

```bash
docker compose start nginx
```

### 重新启动服务

```bash
docker compose restart nginx
```

### 停止正在运行的服务

```bash
docker compose stop nginx
```

### 暂停服务

```bash
docker compose pause nginx
```

### 恢复服务

```bash
docker compose unpause nginx
```

### 删除服务

```bash
docker compose rm nginx
```

### 构建项目

```bash
docker compose build
```

指定服务

```bash
docker compose build nginx
```

`--no-cache` 不使用缓存

```bash
docker compose build --no-cache
```

## 卷（Volume）

### 具体路径 (Bind Mount)

由自己决定容器运行时所需的数据存储在宿主机的具体位置，如下列示例中展示宿主机路径 `/data/myapp`，将该路径的数据挂到容器文件系统中。

```yaml
services:
  myapp:
    image: myapp
    volumes:
      - /data/myapp:/app/data
    ports:
      - "8000:8000"
```

### 具名卷 (Named Volume)

由 Docker 自动管理（通常在 /var/lib/docker/volumes/），对比具体路径优势是跨平台性，可以有效避免不同系统的文件权限体系，隔离性，宿主机数据不易误删。

```yaml
services:
  myapp:
    image: myapp
    volumes:
      - myapp:/app/data
    ports:
      - "8000:8000"

volumes:
  myapp: {}
```

## 网络

### 使用主机网络

```yaml
version: "3"
services:

  app:
    build: .
    image: myapp
    restart: always
    network_mode: host
```
