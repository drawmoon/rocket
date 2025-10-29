# Lab-LLM 🧪

> 一个用于探索、集成与实践各种大语言模型（LLM）工具的实验室，包含 LangChain、LangFlow、LangGraph 等框架的使用示例与实战项目。

---

## 🚀 项目简介

**Lab-LLM** 是一个聚合性实验仓库，旨在帮助开发者快速上手并深入理解 LLM 生态中的核心工具。
本项目从基础的 SDK 调用出发，逐步深入到复杂的工作流设计与应用模式（如 RAG），涵盖 **Prompt 构建、工作流设计、文本解析、智能代理、数据处理** 等方向。

---

## 🧩 涵盖的工具

| 分类 | 工具 / 框架 |
| :--- | :--- |
| **基础集成** | OpenAI SDK, Ollama, LangChain, LiteLLM |
| **工作流编排** | LangFlow, LangGraph |
| **文本提取与解析** | LangExtract |
| **存储与检索** | Chroma, FAISS, Milvus, BM25 |
| **智能应用** | RAG (检索增强生成), Agentic Workflows, Function Calling |

---

## 📂 仓库结构

```bash
Lab-LLM/
├── providers/           # 核心 SDK 调用示例 (OpenAI, Ollama, Google Gemini, LiteLLM, LangChain 等)
├── patterns/            # LLM 应用设计模式
│   ├── rag/             # 检索增强生成 (RAG) 方案示例与知识库集成
│   ├── agents/          # 基于 LangGraph 的多智能体状态机实验
│   └── langextract/     # 结构化数据提取与文本解析实验
├── langflow/            # LangFlow 可视化工作流组件、应用补丁等
└── docs/                # 详细的技术文档与使用说明
