# Rancher

- [Rancher](#rancher)
  - [安装](#安装)
  - [私有注册中心](#私有注册中心)
  - [检查和调试节点上的容器运行时和应用程序](#检查和调试节点上的容器运行时和应用程序)
    - [列出所有 Pod](#列出所有-pod)
    - [列出所有镜像](#列出所有镜像)
    - [列出所有容器](#列出所有容器)

## 安装

安装 MySQL

```bash
docker run -d --name mysql-db -p 3306:3306 -e MYSQL_ROOT_PASSWORD=mysql mysql
```

安装 K3S

```bash
curl -sfL http://rancher-mirror.cnrancher.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn sh -s - server \
  --datastore-endpoint="mysql://root:mysql@tcp(127.0.0.1:3306)/k3s"
```

> 卸载 K3S：`/usr/local/bin/k3s-uninstall.sh`

安装 Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

添加 helm 的 Rancher 源

```bash
helm repo add rancher-stable http://rancher-mirror.oss-cn-beijing.aliyuncs.com/server-charts/stable
```

更新本地 helm 仓库缓存

```bash
helm repo update
```

配置 `KUBECONFIG` 环境变量，helm 通过读取 `KUBECONFIG` 以访问 K3S ApiServer

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

生成证书

> Rancher Server 默认需要 SSL/TLS 配置来保证访问的安全性

```bash
# 安装 Operator Lifecycle Manager
curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.20.0/install.sh | bash -s v0.20.0

# 在集群中安装 cert-manager
kubectl create -f https://operatorhub.io/install/cert-manager.yaml
```

创建命名空间

```bash
kubectl create namespace cattle-system
```

使用 Let's Encrypt 证书验证方式安装 Rancher

```bash
helm install rancher rancher-stable/rancher \
  --namespace cattle-system \
  --set hostname=rancher.test.com \
  --set replicas=1 \
  --set ingress.tls.source=letsEncrypt
```

## 私有注册中心

配置 Docker 客户端允许访问不安全的注册中心

```bash
vi /etc/docker/daemon.json
```

```bash
{
  "insecure-registries": ["docker.k8s"],
}
```

配置 K3S 使用新的注册中心

```bash
vi /etc/rancher/k3s/registries.yaml
```

```bash
mirrors:
  "docker.k8s":
    endpoint:
      - "http://docker.k8s"
configs:
  "docker.k8s":
  auth:
    username: admin
    password: 123456
```

## 检查和调试节点上的容器运行时和应用程序

### 列出所有 Pod

```bash
k3s crictl pods
```

### 列出所有镜像

```bash
k3s crictl images
```

### 列出所有容器

```bash
k3s crictl ps
```
