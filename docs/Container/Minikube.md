- [Minikube](#minikube)
  - [安装](#安装)
    - [Windows](#windows)
  - [启动本地 Kubernetes 集群](#启动本地-kubernetes-集群)

## 安装

### Windows

启用 Hyper-V

以超级管理员身份运行 PowerShell，并执行命令

```bash
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

安装 Minikube

```bash
winget install minikube
```

启动 MiniKube

```bash
minikube start
```

## 启动本地 Kubernetes 集群

```bash
minikube start \
    --iso-url='https://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/iso/minikube-v1.13.0.iso' \
    --image-repository=registry.cn-hangzhou.aliyuncs.com/google_containers
```
