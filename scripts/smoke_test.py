"""
Smoke test: minimal Strands agent on GLM (Z.ai) via LiteLLM.

Run:  uv run python scripts/smoke_test.py
Needs: ZAI_API_KEY (+ optional ZAI_BASE_URL, ZAI_MODEL) in env.
"""
import os
import sys
from strands import Agent, tool
from strands.models.litellm import LiteLLMModel

API_KEY = os.environ.get("ZAI_API_KEY")
BASE_URL = os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/coding/paas/v4")
MODEL_ID = os.environ.get("ZAI_MODEL", "glm-5-turbo")

if not API_KEY:
    sys.exit("ERROR: ZAI_API_KEY not set — export it and retry.")


@tool
def word_count(text: str) -> str:
    """Count words in the given text and return a short summary."""
    n = len(text.split())
    return f"'{text}' has {n} words."


def main() -> None:
    model = LiteLLMModel(
        client_args={"api_key": API_KEY, "api_base": BASE_URL},
        model_id=f"openai/{MODEL_ID}",
        params={"max_tokens": 512, "temperature": 0.2},
    )
    agent = Agent(
        model=model,
        tools=[word_count],
        callback_handler=None,
    )
    result = agent("Use the word_count tool on the sentence 'Agents for Humans rocks' and tell me the result.")
    print("=== RESULT ===")
    print(str(result))
    # sanity: did the agent actually call the tool?
    called = any(
        "toolUse" in u and u["toolUse"].get("name") == "word_count"
        for m in agent.messages
        for u in (m.get("content") or [])
        if isinstance(u, dict)
    )
    print(f"tool_called={called}")
    sys.exit(0 if called else 1)


if __name__ == "__main__":
    main()
