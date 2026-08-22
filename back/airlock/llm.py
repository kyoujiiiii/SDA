"""LLM service — NVIDIA NIM via the OpenAI-compatible SDK, with mock fallback."""

import re
import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from collections import deque

from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL


SYSTEM_PROMPT = """You are a helpful AI assistant specializing in document analysis.

CRITICAL RULES:
1. You MUST keep all bracketed tokens exactly as written: [PERSON_1], [IBAN_1], [EMAIL_1], [PHONE_1], [LOCATION_1], [AHV_1], [AMOUNT_1], etc.
2. Do NOT attempt to guess, fill in, or translate these tokens.
3. Do NOT remove or alter these tokens in any way.
4. These tokens represent sensitive data that will be restored separately.
5. Analyze the document structure and provide insights based on the context around the tokens."""


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Dict[str, int]
    latency_ms: int


@dataclass
class _RateLimiter:
    max_requests: int = 60
    window: int = 60
    _ts: deque = field(default_factory=deque)

    def allowed(self) -> bool:
        now = time.time()
        while self._ts and self._ts[0] < now - self.window:
            self._ts.popleft()
        return len(self._ts) < self.max_requests

    def record(self) -> None:
        self._ts.append(time.time())

    def wait(self) -> float:
        if self.allowed():
            return 0.0
        return max(0.0, self._ts[0] + self.window - time.time())


class LLMService:
    MAX_RETRIES = 3
    BACKOFF = 1.0

    def __init__(self):
        key = LLM_API_KEY
        if key and key not in ("your_nvapi_key_here", ""):
            kwargs = {"api_key": key}
            if LLM_BASE_URL:
                kwargs["base_url"] = LLM_BASE_URL
            self._client = OpenAI(**kwargs)
            self.use_mock = False
            print(f"LLM client ready (nvidia, model={LLM_MODEL})")
        else:
            print("WARNING: No LLM API key set. Using mock mode.")
            self._client = None
            self.use_mock = True

        self._limiter = _RateLimiter()
        self._requests = 0
        self._errors = 0
        self._total_ms = 0

    def chat(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1000) -> LLMResponse:
        if self.use_mock:
            return self._mock(prompt)

        model = model or LLM_MODEL
        if not self._limiter.allowed():
            time.sleep(self._limiter.wait())

        backoff = self.BACKOFF
        last_err = None

        for attempt in range(self.MAX_RETRIES):
            try:
                t0 = time.time()
                resp = self._client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                )
                ms = int((time.time() - t0) * 1000)
                self._limiter.record()
                self._requests += 1
                self._total_ms += ms

                usage = resp.usage
                return LLMResponse(
                    content=resp.choices[0].message.content or "",
                    model=resp.model or model,
                    usage={
                        "prompt_tokens": usage.prompt_tokens if usage else 0,
                        "completion_tokens": usage.completion_tokens if usage else 0,
                        "total_tokens": usage.total_tokens if usage else 0,
                    },
                    latency_ms=ms,
                )

            except (RateLimitError, APIConnectionError) as e:
                last_err = e
                self._errors += 1
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    raise

            except APIError as e:
                self._errors += 1
                if 400 <= e.status_code < 500 and e.status_code != 429:
                    raise
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    raise

        raise last_err or Exception("Max retries exceeded")

    def _mock(self, prompt: str) -> LLMResponse:
        tokens = re.findall(r"\[[A-Z]+_\d+\]", prompt)
        if tokens:
            t = ", ".join(tokens[:5])
            content = (
                f"Analysis of {t}:\n\n"
                f"1. All referenced entities identified.\n"
                f"2. Data is consistent with standard business practices.\n"
                f"3. No anomalies detected.\n\n"
                f"Entities {t} are properly referenced. Recommendation: proceed with verification."
            )
        else:
            content = (
                "Request analyzed successfully.\n\n"
                "Key findings:\n"
                "- All data within expected parameters\n"
                "- No sensitive information anomalies\n"
                "- Document structure standard"
            )
        return LLMResponse(
            content=content,
            model="mock-llama-3.1-8b-instruct",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            latency_ms=5,
        )

    def get_stats(self) -> Dict:
        return {
            "mode": "mock" if self.use_mock else "nvidia",
            "total_requests": self._requests,
            "total_errors": self._errors,
            "avg_latency_ms": self._total_ms // self._requests if self._requests else 0,
        }


llm_service = LLMService()
