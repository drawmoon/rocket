LLM, RAG, Agentic Workflow



前言
---

这份文档主要内容是说明一个从零构建现代 AI 系统的方法论指南，文档主要以 LLM, RAG, Agentic Workflow 贯穿从单一的大模型 API 调用，到具备“手脚”（Function Calling）、“眼耳”（多模态）、“大脑库”（RAG）以及“独立思考逻辑”（Agentic Workflow）的技术路线演进，以及各个组成部分的基本概念，和如何结合主流的如 LiteLLM、LangChain 和 DSPy 等生态工具快速入手。

仓库使用 Markdown 作为主文档，主要包含基本概念和演进路线，安装示例与代码示例则在 Notebook 中，在 Notebook 中可以更加清晰的查看安装步骤或代码块执行时输出的结果，你也可以手动更改代码并运行代码块来实时查看模型输出。

Notebook 中的示例需要调用大模型，示例中的模型提供商是均是 Google AI Studio，且使用 OpenAI 兼容的方式调用，你可以根据自己的硬件条件选择以下方式运行，一个是在本机部署 Ollama 或使用 Google AI Studio 的免费额度 

- 本地私有化部署 (Ollama)
  如果你拥有性能较好的 GPU，跳转到 [什么是 Ollama](#什么是-ollama) 查看如何安装 Ollama，安装 Ollama 成功后，将代码中的 API Base 地址指向 `http://localhost:11434/v1` 即可，或者使用 CPU 进行模型推理。
- Google AI Studio
  Google AI Studio 提供了免费的 API 调用额度调用 Gemini 系列模型。
- 或在本地使用 Transformers 或 vLLM 等推理平台，只需要更改示例中 API Base 和 API Key 即可。



概述
---

- 
- 什么是 LLM
  - 什么是 Ollama
- 什么是 RAG
  - 什么是 Rerank
  - 如何结合 RAG 和 DSPy
- 什么是 Agentic Workflow
- 



什么是 LLM
---

LLM 是 Large Language Model 的缩写，翻译过来是大语言模型，简单来说，它是一种基于深度学习的人工智能系统，专门用于理解、生成和处理人类语言。从底层的技术逻辑来看，LLM 本质上是一个基于统计学的超大规模高维概率预测引擎。



### PyTorch 与手动推理
在开发范式 OpenAI 之前，传统的 LLM 调用范式，是在 PyTorch 或 TensorFlow 框架下直接操作 Transformer 模型。在 NLP 的演进史上更具有代表性，以 HanLP 为例，HanLP 代表的是 “符号工程与深度学习过渡期” 的典型调用方式。在 API 时代之前，模型就是“代码+权重”，开发者必须处理张量。

- 核心概念：流水线 (Pipeline)
  传统 NLP 认为理解语言需要分步骤进行。HanLP 提供的典型调用方式是创建一个 Pipeline（或称为 Annotation），将文本流依次通过不同的算子。

[Transformers Notebook 代码示例](Transformers.ipynb)

在这段代码中，虽然使用了现代的 Transformers 库，但其核心思想契合了传统 NLP 任务导向与底层算子解构的逻辑。

但对于现在绝大多数应用开发者来说，最原始的调用是指 OpenAI 风格的 HTTP 调用。


> 接下来，我们是否需要探讨一下，现在的 LangExtract 这种工具是如何利用 LLM 的生成能力，反过来实现 HanLP 曾经擅长的结构化提取任务的？



什么是 Ollama
---

Ollama 是一个开源项目，目的是简化在本地机器上运行大型语言模型（LLMs）的过程。它提供用户友好的界面和功能，使先进的人工智能技术变得易于获取且可定制。

安装 Ollama:
```sh
curl -fsSL https://ollama.com/install.sh | sh
```

> 如果你发现 Ollama 没有默认调用你的 GPU，或者你通过容器运行 Ollama，你可以通过设置此变量来显式设置 GPU 的分配策略。
> 
> 操作步骤：
> - 设置环境变量：`export OLLAMA_NUM_GPU=-1`
> - 启动 Ollama：`ollama serve`

Ollama 安装好后可以通过 `ollama list` 查看可用模型。

查看如何安装 Ollama，使用 Ollama SDK 以及兼容 OpenAI 的方式调用 Ollama 服务，请点击 [Ollama Notebook](Ollama.ipynb) 查看 Notebook 代码块运行结果以及查看模型输出。


**为 Ollama 配置 AMD 显卡加速**

在 Linux 环境下为 Ollama 配置 AMD 显卡支持时，请注意以下几点：

> 以 Ubuntu 24.04 为例。

1. ROCm 驱动版本
   确保系统中已安装兼容的 ROCm 运行库。Ollama 通常需要 ROCm 驱动和软件栈，AMD 显卡通过 ROCm 平台提供 GPU 加速支持。
```sh
wget https://repo.radeon.com/amdgpu-install/6.4.3/ubuntu/noble/amdgpu-install_6.4.60403-1_all.deb
sudo apt install ./amdgpu-install_6.4.60403-1_all.deb
sudo apt update
sudo apt install python3-setuptools python3-wheel
sudo usermod -a -G render,video $LOGNAME # 必须将当前用户添加到 render 和 video 用户组，否则 Ollama 进程可能无法调用 GPU 硬件
sudo apt install rocm
```

2. 安装 AMD GPU 驱动
```sh
wget https://repo.radeon.com/amdgpu-install/6.4.3/ubuntu/noble/amdgpu-install_6.4.60403-1_all.deb
sudo apt install ./amdgpu-install_6.4.60403-1_all.deb
sudo apt update
sudo apt install "linux-headers-$(uname -r)" "linux-modules-extra-$(uname -r)"
sudo apt install amdgpu-dkms
```

3. 驱动环境变量
   如果你的 GPU 属于较旧系列（如 RDNA 1 代），可能需要设置环境变量来强制兼容：
   `export HSA_OVERRIDE_GFX_VERSION=10.3.0`

4. 显存分配
   AMD 显卡在 Linux 下的显存管理较为严格，建议关闭系统桌面环境的硬件加速或增加 Swap 空间，以防止加载大参数模型时发生显存溢出（OOM）。

5. 验证是否启用 GPU：
   安装支持 ROCm 的 PyTorch：
```sh
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.4
```
   测试 GPU 是否启用，执行代码应输出 True（ROCm 模拟 CUDA 接口）：
```py
import torch
print(torch.cuda.is_available())
```

6. 配置 Ollama 使用 AMD GPU 加速：
   `export OLLAMA_AMDGPU=1`













