#!/usr/bin/env python3
"""
Utility script to verify connectivity to DeepSeek and Qwen OpenAI-compatible endpoints.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from openai.error import OpenAIError

load_dotenv()


@dataclass
class ProviderProbe:
    """Configuration data for one OpenAI-compatible provider."""

    name: str
    api_key: str
    model: str
    base_url: Optional[str]

    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)


def build_providers() -> List[ProviderProbe]:
    """Create provider configs from environment variables with sensible defaults."""
    return [
        ProviderProbe(
            name="DeepSeek",
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        ),
        ProviderProbe(
            name="Qwen",
            api_key=os.getenv("QWEN_API_KEY", ""),
            model=os.getenv("QWEN_MODEL", "qwen-plus"),
            base_url=os.getenv(
                "QWEN_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        ),
    ]


def test_provider(provider: ProviderProbe) -> Dict[str, str]:
    """Ping the provider with a lightweight chat completion."""
    if not provider.is_configured():
        return {
            "status": "skipped",
            "detail": "missing API key or model",
        }

    client_args: Dict[str, str] = {"api_key": provider.api_key}
    if provider.base_url:
        client_args["base_url"] = provider.base_url

    client = OpenAI(**client_args)

    payload = {
        "model": provider.model,
        "messages": [
            {"role": "system", "content": "This is a connection check."},
            {"role": "user", "content": "Ping from the RAG system health check."},
        ],
        "temperature": 0,
        "max_tokens": 5,
    }

    try:
        response = client.chat.completions.create(**payload)
    except OpenAIError as err:
        return {
            "status": "failure",
            "detail": str(err),
        }

    choice = response.choices[0]
    content = choice.message.content or ""
    return {"status": "success", "detail": content.strip()}


def main() -> None:
    probes = build_providers()
    results = []
    for probe in probes:
        result = test_provider(probe)
        results.append((probe.name, result))

    for name, result in results:
        status = result["status"]
        detail = result["detail"]
        print(f"{name}: {status.upper()} - {detail}")


if __name__ == "__main__":
    main()
