---
name: image-sense
description: 通过多模态模型识图，返回纯文字。当需要"看图"时使用——主 Agent 是纯文字模型，把本地路径或 base64 图片 + 一句话/预设模式丢给 OpenAI 兼容的多模态模型，拿回文字结论。常用于描述图片、OCR 提取文字、图表解读、多图对比、自定义识图提问。
---

# image-sense — 视觉传感器

给纯文字主 Agent 挂一个识图能力：输入图片（路径或 base64），输出 VLM 返回的文字结论。主模型不必是多模态，只有真正需要看图时才经此调用多模态模型，省钱。

## 环境变量（`.env` 用 `load_dotenv()` 读取）

```bash
IMAGE_SENSE_BASE_URL=https://api.moonshot.cn/v1   # 或 openai / dashscope 等
IMAGE_SENSE_API_KEY=sk-xxx
IMAGE_SENSE_MODEL=kimi-k2-visual                   # 视觉模型名
```

## 用法

```bash
python scripts/image-sense.py \
  --images a.png b.jpg "iVBORw0KGgo..." \   # 路径或 base64，支持混传多张
  --mode describe                            # describe/contents/ocr/chart
  --question "自定义问题"                     # 给了覆盖 --mode
  --detail standard                          # brief/standard/detailed
  --reasoning-effort high                    # 思考强度（OpenAI/Kimi 系）
  --enable-thinking                          # 开思考（Qwen 系）
  --thinking-budget 2048                     # 思考 token 上限（Qwen 系）
```

输出：stdout 直接打印 VLM 文字。失败时非零退出码 + stderr 报错。

## 参数

| 参数 | 说明 |
|------|------|
| `--images`（必填） | `nargs='+'`，本地路径（`~/x.png`/`/abs/x.jpg`）或 base64，可混传多张 |
| `--mode` | 预设模式：`describe`/`contents`/`ocr`/`chart`，默认 `describe` |
| `--question` | 自定义问题，给了就覆盖 `--mode` |
| `--detail` | `brief`/`standard`/`detailed`，默认 `standard` |
| `--reasoning-effort` | `low`/`medium`/`high`，仅 OpenAI/Kimi 系模型支持时生效 |
| `--enable-thinking` | 布尔，仅 Qwen 系模型支持时生效 |
| `--thinking-budget` | 整型，仅 Qwen 系模型支持时生效 |

## 思考参数健壮性

三个思考参数按**模型名白名单**注入，模型不支持时**静默忽略**，绝不因传参导致调用失败：

- `reasoning_effort` → 模型名含 `gpt-5`/`gpt-4`/`k2`/`kimi`
- `enable_thinking` + `thinking_budget` → 模型名含 `qwen`
- 两者互斥，各自独立判断

## 示例

```bash
# 单图描述
python scripts/image-sense.py --images ./shot.png

# 多图 OCR
python scripts/image-sense.py --images a.png b.png c.png --mode ocr

# 图表详细解读
python scripts/image-sense.py --images kline.png --mode chart --detail detailed

# 多图对比（自定义问题）
python scripts/image-sense.py --images dA.png dB.png --question "这两张界面图的主要差异？"

# Qwen 开思考 + 限制思考 token 预算
python scripts/image-sense.py --images img.png --enable-thinking --thinking-budget 2048

# base64 直接传
python scripts/image-sense.py --images "iVBORw0KGgo..." --question "图里是什么"
```

## 说明

- 输入层：`--images` 每项自动识别是 data URI / 本地路径 / 裸 base64，统一转成字节 + mime，再拼成 OpenAI 兼容的 `image_url`(base64 data URI)。三家（OpenAI/Kimi/Qwen）都认 base64。