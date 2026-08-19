#!/usr/bin/env python3
"""dsh_task.py — запуск одной агентной задачи через DeepSeek Harness SDK.

Требует: deepseek-harness-sdk (pip install), DEEPSEEK_API_KEY или
DEEPSEEK_BASE_URL (OpenAI-совместимый endpoint).

Пример:
  DEEPSEEK_API_KEY=sk-... python3 dsh_task.py \
    --workspace /tmp/ws/repo --session-root /tmp/sessions \
    --session-id fix-001 "Почини падающий тест."

Exit codes: 0 = задача завершена (final_response есть), 2 = ошибка запуска.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a single agent task via DeepSeek Harness SDK")
    p.add_argument("--workspace", required=True, help="absolute path to the task workspace (agent's cwd)")
    p.add_argument("--session-root", required=True, help="absolute path where session logs are stored")
    p.add_argument("--session-id", default="task-001", help="unique session id (per task)")
    p.add_argument("--model", default=None, help="model id; default from DSH_MODEL or deepseek-v4-flash")
    p.add_argument("--provider", default=None, help="provider id; default 'deepseek-official'")
    p.add_argument("--max-tokens", type=int, default=49152, help="max model tokens per task")
    p.add_argument("--cordis", default=None, help="path to cordis composition yml (jsonrpc-agent minimal by default)")
    p.add_argument("prompt", help="the task prompt for the agent")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace).resolve()
    session_root = Path(args.session_root).resolve()
    session_root.mkdir(parents=True, exist_ok=True)

    if not workspace.is_dir():
        print(f"[dsh_task] workspace does not exist: {workspace}", file=sys.stderr)
        return 2
    if not os.environ.get("DEEPSEEK_API_KEY") and not os.environ.get("DEEPSEEK_BASE_URL"):
        print("[dsh_task] set DEEPSEEK_API_KEY or DEEPSEEK_BASE_URL first", file=sys.stderr)
        return 2

    model = args.model or os.environ.get("DSH_MODEL", "deepseek-v4-flash")
    provider = args.provider or os.environ.get("DSH_PROVIDER", "deepseek-official")

    try:
        from deepseek_harness import DeepSeekHarness  # type: ignore
    except ImportError:
        print("[dsh_task] pip install deepseek-harness-sdk first", file=sys.stderr)
        return 2

    kwargs: dict = {
        "provider": provider,
        "model": model,
        "max_tokens": args.max_tokens,
        "cwd": str(workspace),
        "session_root": str(session_root),
    }
    if args.cordis:
        kwargs["cordis"] = args.cordis

    print(f"[dsh_task] workspace={workspace} model={model} session_id={args.session_id}")
    try:
        with DeepSeekHarness(**kwargs) as harness:
            result = harness.run(args.prompt, session_id=args.session_id)
    except Exception as exc:  # SDK is preview; surface raw error
        print(f"[dsh_task] harness error: {exc}", file=sys.stderr)
        return 2

    report = {
        "session_id": getattr(result, "session_id", args.session_id),
        "final_response": getattr(result, "final_response", ""),
        "finish_reason": getattr(result, "finish_reason", None),
        "session_root": str(session_root),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
