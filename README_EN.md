<div align="center">

# image-sense.skill

A "visual sensor" for text-only primary Agents — invoke a multimodal model only when you actually need to look at an image, and get back plain-text conclusions ✨

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple?logo=robot&logoColor=white)](https://github.com/openclaw/openclaw)
[![QwenPaw](https://img.shields.io/badge/Qwenpaw-Skill-orange?logo=robot&logoColor=white)](https://github.com/agentscope-ai/QwenPaw)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-brightgreen?logo=anthropic&logoColor=white)](https://claude.ai/code)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI_SDK-1.x-green)](https://github.com/openai/openai-python)
[![dotenv](https://img.shields.io/badge/python--dotenv-1.x-orange)](https://github.com/theskumar/python-dotenv)

[**简体中文**](README.md) | English

</div>

---

## ✨ Features

- 👁️ **Vision on demand** - The primary Agent doesn't need to be multimodal; call a VLM only when an image truly needs reading — saves money
- 🖼️ **Multi-image input** - Mix local paths / data URIs / raw base64 in a single call, format auto-detected
- 🎯 **Preset modes** - `describe` / `contents` (object list) / `ocr` / `chart` interpretation
- ❓ **Custom questions** - Free-form `--question`, supports multi-image comparison
- 🧠 **Thinking-parameter whitelist** - `reasoning_effort` / `enable_thinking` injected by model name; silently ignored when unsupported
- 🔌 **OpenAI-compatible** - One codebase works with Kimi / Qwen / OpenAI / DashScope and any compatible endpoint

---

## 🚀 Quick Start

### 📦 Installation

```bash
# 1. Install Python dependencies
pip install openai python-dotenv

# 2. Install the skill to your platform

# Claude Code
cp -r skills/image-sense ~/.claude/skills/image-sense

# OpenClaw
cp -r skills/image-sense ~/.openclaw/skills/image-sense

# QwenPaw
cp -r skills/image-sense ~/.copaw/skill_pool/image-sense
```

### ⚙️ Configuration

Create a `.env` file in the skill directory (loaded automatically via `load_dotenv()`):

```bash
IMAGE_SENSE_BASE_URL=https://api.moonshot.cn/v1   # or OpenAI / DashScope / any compatible endpoint
IMAGE_SENSE_API_KEY=sk-xxx
IMAGE_SENSE_MODEL=kimi-k2-visual                   # vision model name
```

### 🎮 Basic Usage

**Option 1: Install as a platform skill (recommended)**

Use directly in your platform's conversation:

```
/image-sense --images ./shot.png
/image-sense --images a.png b.png --mode ocr
/image-sense --images kline.png --mode chart --detail detailed
```

**Option 2: Run the script directly (for testing/debugging)**

```bash
# Enter the script directory
cd skills/image-sense/scripts

# Show help 👀
python image-sense.py --help

# Describe a single image 📷
python image-sense.py --images ./shot.png

# Custom question ❓
python image-sense.py --images dA.png dB.png --question "What are the main differences between these two UI screenshots?"
```

Output: the VLM's text conclusion is printed to stdout; on failure, a non-zero exit code plus an error on stderr.

---

## 📖 Usage Guide

### 🔧 Parameters

| Parameter | Description |
|-----------|-------------|
| `--images` | 🖼️ Required, `nargs='+'`; local paths (`~/x.png`/`/abs/x.jpg`) or base64, mixable across multiple images |
| `--mode` | 🎯 Preset mode: `describe`/`contents`/`ocr`/`chart`, default `describe` |
| `--question` | ❓ Custom question; overrides `--mode` when provided |
| `--detail` | 📝 Verbosity: `brief`/`standard`/`detailed`, default `standard` |
| `--reasoning-effort` | 🧠 Reasoning effort `low`/`medium`/`high` (OpenAI/Kimi family) |
| `--enable-thinking` | 💭 Enable thinking (Qwen family) |
| `--thinking-budget` | ⏱️ Thinking token budget (Qwen family) |

### 🧠 Thinking-Parameter Robustness

The three thinking parameters are injected via a **model-name whitelist**; unsupported parameters are **silently ignored** — a call never fails because of them:

| Parameter | Effective when the model name contains |
|-----------|----------------------------------------|
| `reasoning_effort` | `gpt-5` / `gpt-4` / `k2` / `kimi` |
| `enable_thinking` + `thinking_budget` | `qwen` |

The two groups are mutually exclusive and evaluated independently.

### 💡 Examples

```bash
# 📷 Describe a single image
python image-sense.py --images ./shot.png

# 📝 OCR across multiple images
python image-sense.py --images a.png b.png c.png --mode ocr

# 📊 Detailed chart interpretation
python image-sense.py --images kline.png --mode chart --detail detailed

# 🔀 Multi-image comparison (custom question)
python image-sense.py --images dA.png dB.png --question "What are the main differences between these two UI screenshots?"

# 💭 Qwen with thinking enabled + token budget
python image-sense.py --images img.png --enable-thinking --thinking-budget 2048

# 📦 Pass base64 directly
python image-sense.py --images "iVBORw0KGgo..." --question "What's in this image?"
```

---

## 🖼️ Supported Image Formats

| Format | Detection |
|:------:|-----------|
| PNG | Extension / magic bytes `\x89PNG` |
| JPEG | Extension / magic bytes `\xFF\xD8` |
| WebP | Extension / magic bytes `RIFF` |
| GIF | Extension / magic bytes `GIF8` |
| BMP | Extension / magic bytes `BM` |

Each input is auto-detected as data URI / local path / raw base64, normalized to bytes + mime, and assembled into an OpenAI-compatible `image_url` (base64 data URI) — all three providers (OpenAI/Kimi/Qwen) accept base64.

---

## ⚠️ Notes

> 🔑 **API configuration**: `IMAGE_SENSE_API_KEY` and `IMAGE_SENSE_MODEL` must be set, otherwise the script exits with an error

> 💰 **Cost reminder**: Multimodal calls are billed by token; higher image resolution costs more — call only when vision is truly needed

> 🌐 **Compatibility**: Requires an OpenAI-compatible Chat Completions endpoint with a vision model that supports `image_url`

> 🚫 **Rate limits**: Don't hammer the API — avoid triggering provider rate limiting

---

<div align="center">

### 🌟 If this project helps you, please give it a Star!

Made with ❤️ for text-only agents

</div>
