## 简介

Podman 完全兼容 Docker 命令，你可以像使用 Docker 一样使用 Podman，例如：`podman images`。

Podman vs Docker:
- 无需进程守护
- 无需 Root 权限，原生支持 Rootless 普通用户即可运行
- CLI 直接调用 runc
- 支持将多个容器组合成 Pod（类似 Kubernetes）

Podman 默认不支持镜像名称的简写，需要全名称，例如：
```sh
podman pull docker.io/library/alpine
podman pull docker.io/library/alpine:3.19
```

安装 Podman:
```sh
sudo apt update
sudo apt install -y podman
```

### Podman 后续环境配置

#### 配置镜像加速

创建 `registries.conf` 配置文件:
```sh
mkdir -p ~/.config/containers
vim ~/.config/containers/registries.conf
```

填入如下内容:
```toml
unqualified-search-registries = ["docker.io", "quay.io"]

[[registry]]
prefix = "docker.io"
location = "f1361db2.m.daocloud.io"
```

#### 解决挂载传播警告

当你作为普通用户运行 Podman 时，Podman 会创建一个属于你的用户命名空间执行 podman 命令时，系统可能会提示 `WARN[0000] "/" is not a shared mount, this could cause issues or missing mounts with rootless containers`。

这是因为宿主机的根目录默认挂载属性为 `private`，在 Rootless 模式下，Podman 需要根路径为 `shared`，以便在容器命名空间和宿主机之间同步挂载点。

在完成 Podman 安装后，为了确保 Rootless 容器能够正确挂载卷并避免权限传播问题，必须执行以下配置。

查看根目录传播:
```sh
findmnt -o TARGET,PROPAGATION /
```

默认情况下你会看到输出结果是 `/ private`:
```
TARGET PROPAGATION
/ private
```

创建一个 Systemd 服务，在系统每次启动时自动设置根目录为 `shared`:
```sh
sudo vim /etc/systemd/system/make-root-shared.service
```

填入如下内容:
```
[Unit]
Description=Make root filesystem shared for Podman
Before=docker.service podman.service

[Service]
Type=oneshot
ExecStart=/usr/bin/mount --make-rshared /
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

加载配置:
```sh
sudo systemctl daemon-reload
```

设置开机自启并立即启动:
```sh
sudo systemctl enable --now make-root-shared.service
```

执行 `findmnt -o TARGET,PROPAGATION /` 验证根目录是否已经输出 `shared`


### Podman Compose：

安装 podman-compose:
```sh
sudo apt install podman-compose
```

或者使用 pip 安装:
```sh
pip install podman-compose
```

Podman Compose 也与 Docker Compose 完全兼容。
