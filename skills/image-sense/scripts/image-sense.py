#!/usr/bin/env python3
"""image-sense —— 给纯文字主 Agent 挂一个"视觉传感器"。

输入任意多张图（本地路径或 base64），预设模式或自定义问题，
调用 OpenAI 兼容的多模态模型，输出纯文字结论。

配置走 .env（load_dotenv）：
    IMAGE_SENSE_BASE_URL  供应商接口地址
    IMAGE_SENSE_API_KEY   API key
    IMAGE_SENSE_MODEL     视觉模型名
"""
import argparse
import base64
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("IMAGE_SENSE_BASE_URL")
API_KEY = os.getenv("IMAGE_SENSE_API_KEY")
MODEL = os.getenv("IMAGE_SENSE_MODEL")

EXT_MIME = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
}
MAGIC_MIME = {
    b"\x89PNG": "image/png", b"\xff\xd8": "image/jpeg",
    b"RIFF": "image/webp", b"GIF8": "image/gif", b"BM": "image/bmp",
}

MODES = {
    "describe": "请描述这张图片。",
    "contents": "这张图片里有什么？列出主体/物体清单。",
    "ocr": "请提取图中所有文字，原样输出。",
    "chart": "请解读这张图表：趋势、关键数值、坐标读数。",
}

DETAILS = {
    "brief": "回答尽量简短。",
    "standard": "",
    "detailed": "回答尽量详尽，给出细节。",
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="image-sense",
        description="通过多模态模型识图，返回纯文字。",
    )
    p.add_argument("--images", nargs="+", required=True,
                   help="图片：本地路径（~/x.png 或 /abs/x.jpg）或 base64 字符串，支持混传多张")
    p.add_argument("--mode", default="describe",
                   choices=list(MODES), help="预设模式（默认 describe）")
    p.add_argument("--question", default=None,
                   help="自定义问题，给了就覆盖 --mode")
    p.add_argument("--detail", default="standard",
                   choices=list(DETAILS), help="详细度")
    p.add_argument("--reasoning-effort", default=None,
                   choices=["low", "medium", "high"],
                   help="思考强度（仅 OpenAI/Kimi 系认证支持时生效）")
    p.add_argument("--enable-thinking", action="store_true",
                   help="开启思考（仅 Qwen 系认证支持时生效）")
    p.add_argument("--thinking-budget", type=int, default=None,
                   help="思考 token 上限（仅 Qwen 系认证支持时生效）")
    return p


def _bytes_to_mime(b: bytes) -> str:
    for magic, mime in MAGIC_MIME.items():
        if b.startswith(magic):
            return mime
    return "image/png"


def _to_payload(src: str, idx: int) -> dict:
    """任一图片输入（路径或 base64）-> {index, path, mime, data}"""
    src = os.path.expanduser(src)
    if src.startswith("data:"):                        # data URI
        meta, _, b64 = src[5:].partition(",")
        mime = meta.split(";")[0]
        data = base64.b64decode(b64)
    elif os.path.exists(src):                          # 本地路径
        data = Path(src).read_bytes()
        mime = EXT_MIME.get(Path(src).suffix.lower()) or _bytes_to_mime(data)
    else:                                              # 裸 base64
        data = base64.b64decode(src)
        mime = _bytes_to_mime(data)
    return {"index": idx, "path": src, "mime": mime, "data": data}


def load_images(images) -> list:
    """多图收口：逐项归一化，顺序编号。"""
    return [_to_payload(s, i) for i, s in enumerate(images)]


def build_question(args) -> str:
    if args.question:
        q = args.question
    else:
        fig = ", ".join(f"图{i}" for i in range(len(args.images)))
        q = f"{MODES[args.mode]}（{fig}）"
    detail = DETAILS[args.detail]
    return f"{q}\n{detail}".strip()


def thinking_params(model: str, args) -> dict:
    """按模型白名单注入思考字段。不支持的字段一律不写，绝不报错。"""
    m = model.lower()
    params = {}
    if args.reasoning_effort and ("gpt-5" in m or "gpt-4" in m or "k2" in m or "kimi" in m):
        params["reasoning_effort"] = args.reasoning_effort
    if "qwen" in m:
        if args.enable_thinking:
            params["enable_thinking"] = True
        if args.thinking_budget is not None:
            params["thinking_budget"] = args.thinking_budget
    return params


def to_openai_content(payloads, prompt: str) -> dict:
    parts = [{"type": "text", "text": prompt}]
    for p in payloads:
        uri = f"data:{p['mime']};base64,{base64.b64encode(p['data']).decode()}"
        parts.append({"type": "image_url", "image_url": {"url": uri}})
    return {"role": "user", "content": parts}


def main() -> int:
    args = build_parser().parse_args()
    if not API_KEY or not MODEL:
        print("错误：请设置 IMAGE_SENSE_API_KEY 和 IMAGE_SENSE_MODEL（.env 或环境变量）", file=sys.stderr)
        return 1

    try:
        payloads = load_images(args.images)
    except Exception as e:
        print(f"错误：图片加载失败 - {e}", file=sys.stderr)
        return 1

    prompt = build_question(args)

    try:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        payload = {
            "model": MODEL,
            "messages": [to_openai_content(payloads, prompt)],
        }
        # 思考参数走 extra_body 透传：SDK 不做参数校验，直接进请求体，
        # 不支持的字段在 thinking_params 里已过滤，绝不因传参导致调用失败。
        resp = client.chat.completions.create(
            **payload, extra_body=thinking_params(MODEL, args)
        )
        text = resp.choices[0].message.content
    except Exception as e:
        print(f"错误：模型调用失败 - {e}", file=sys.stderr)
        return 1

    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())