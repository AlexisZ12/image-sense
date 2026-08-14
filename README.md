<div align="center">

# 图像感知.skill

给纯文字主 Agent 挂一个"视觉传感器"——需要看图时才调用多模态模型，返回纯文字结论 ✨

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple?logo=robot&logoColor=white)](https://github.com/openclaw/openclaw)
[![QwenPaw](https://img.shields.io/badge/Qwenpaw-Skill-orange?logo=robot&logoColor=white)](https://github.com/agentscope-ai/QwenPaw)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-brightgreen?logo=anthropic&logoColor=white)](https://claude.ai/code)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI_SDK-1.x-green)](https://github.com/openai/openai-python)
[![dotenv](https://img.shields.io/badge/python--dotenv-1.x-orange)](https://github.com/theskumar/python-dotenv)

简体中文 | [**English**](README_EN.md)

</div>

---

## ✨ 功能特性

- 👁️ **按需识图** - 主 Agent 不必是多模态，只有真正需要看图时才调用 VLM，省钱
- 🖼️ **多图输入** - 本地路径 / data URI / 裸 base64 混传多张，自动识别格式
- 🎯 **预设模式** - `describe` 描述 / `contents` 物体清单 / `ocr` 文字提取 / `chart` 图表解读
- ❓ **自定义提问** - `--question` 自由提问，支持多图对比
- 🧠 **思考参数白名单** - `reasoning_effort` / `enable_thinking` 按模型名自动注入，不支持静默忽略
- 🔌 **OpenAI 兼容** - 一套代码通吃 Kimi / Qwen / OpenAI / DashScope 等兼容接口

---

## 🚀 快速开始

### 📦 安装

```bash
# 1. 安装 Python 依赖
pip install openai python-dotenv

# 2. 将技能安装到对应平台

# Claude Code
cp -r skills/image-sense ~/.claude/skills/image-sense

# OpenClaw
cp -r skills/image-sense ~/.openclaw/skills/image-sense

# QwenPaw
cp -r skills/image-sense ~/.copaw/skill_pool/image-sense
```

### ⚙️ 配置

在技能目录创建 `.env` 文件（`load_dotenv()` 自动读取）：

```bash
IMAGE_SENSE_BASE_URL=https://api.moonshot.cn/v1   # 或 OpenAI / DashScope 等兼容接口
IMAGE_SENSE_API_KEY=sk-xxx
IMAGE_SENSE_MODEL=kimi-k2-visual                   # 视觉模型名
```

### 🎮 基本用法

**方式一：安装为平台技能（推荐）**

在对应平台对话中直接使用：

```
/image-sense --images ./shot.png
/image-sense --images a.png b.png --mode ocr
/image-sense --images kline.png --mode chart --detail detailed
```

**方式二：直接运行脚本（测试/调试用途）**

```bash
# 进入脚本目录
cd skills/image-sense/scripts

# 查看帮助 👀
python image-sense.py --help

# 单图描述 📷
python image-sense.py --images ./shot.png

# 自定义问题 ❓
python image-sense.py --images dA.png dB.png --question "这两张界面图的主要差异？"
```

输出：stdout 直接打印 VLM 文字结论；失败时非零退出码 + stderr 报错。

---

## 📖 使用指南

### 🔧 参数说明

| 参数 | 说明 |
|------|------|
| `--images` | 🖼️ 必填，`nargs='+'`，本地路径（`~/x.png`/`/abs/x.jpg`）或 base64，可混传多张 |
| `--mode` | 🎯 预设模式：`describe`/`contents`/`ocr`/`chart`，默认 `describe` |
| `--question` | ❓ 自定义问题，给了就覆盖 `--mode` |
| `--detail` | 📝 详细度：`brief`/`standard`/`detailed`，默认 `standard` |
| `--reasoning-effort` | 🧠 思考强度 `low`/`medium`/`high`（OpenAI/Kimi 系） |
| `--enable-thinking` | 💭 开启思考（Qwen 系） |
| `--thinking-budget` | ⏱️ 思考 token 上限（Qwen 系） |

### 🧠 思考参数健壮性

三个思考参数按**模型名白名单**注入，模型不支持时**静默忽略**，绝不因传参导致调用失败：

| 参数 | 生效条件（模型名包含） |
|------|----------------------|
| `reasoning_effort` | `gpt-5` / `gpt-4` / `k2` / `kimi` |
| `enable_thinking` + `thinking_budget` | `qwen` |

两者互斥，各自独立判断。

### 💡 使用示例

```bash
# 📷 单图描述
python image-sense.py --images ./shot.png

# 📝 多图 OCR
python image-sense.py --images a.png b.png c.png --mode ocr

# 📊 图表详细解读
python image-sense.py --images kline.png --mode chart --detail detailed

# 🔀 多图对比（自定义问题）
python image-sense.py --images dA.png dB.png --question "这两张界面图的主要差异？"

# 💭 Qwen 开思考 + 限制思考 token 预算
python image-sense.py --images img.png --enable-thinking --thinking-budget 2048

# 📦 base64 直接传
python image-sense.py --images "iVBORw0KGgo..." --question "图里是什么"
```

---

## 🖼️ 支持的图片格式

| 格式 | 识别方式 |
|:----:|----------|
| PNG | 扩展名 / 魔数 `\x89PNG` |
| JPEG | 扩展名 / 魔数 `\xFF\xD8` |
| WebP | 扩展名 / 魔数 `RIFF` |
| GIF | 扩展名 / 魔数 `GIF8` |
| BMP | 扩展名 / 魔数 `BM` |

输入层每项自动识别 data URI / 本地路径 / 裸 base64，统一转成字节 + mime，拼成 OpenAI 兼容的 `image_url`（base64 data URI）——三家（OpenAI/Kimi/Qwen）都认 base64。

---

## ⚠️ 注意事项

> 🔑 **API 配置**：必须设置 `IMAGE_SENSE_API_KEY` 和 `IMAGE_SENSE_MODEL`，否则脚本直接报错退出

> 💰 **费用提示**：多模态调用按 token 计费，图片分辨率越高费用越高，建议仅在确需看图时调用

> 🌐 **接口兼容**：需要 OpenAI 兼容的 Chat Completions 接口且支持 `image_url` 的视觉模型

> 🚫 **请求频率**：请勿频繁请求，以免触发供应商限流

---

<div align="center">

### 🌟 如果这个项目对你有帮助，欢迎 Star！

Made with ❤️ for text-only agents

</div>
