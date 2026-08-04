import logging
import os
import random
import asyncio
import time
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class OpenRouterConfigError(Exception):
    pass

class OpenRouterClient:
    _semaphore = None
    _shared_client = None

    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self._model = model or os.getenv("OPENROUTER_MODEL") or "meta-llama/llama-3.1-8b-instruct:free"
        self._base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self._max_retries = int(os.getenv("OPENROUTER_MAX_RETRIES", "5"))
        self._timeout = float(os.getenv("OPENROUTER_TIMEOUT", "60.0"))
        self._max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "900"))
        self._use_json_mode = os.getenv("OPENROUTER_USE_JSON_MODE", "True").lower() in ("true", "1", "yes")
        
        concurrency = int(os.getenv("OPENROUTER_CONCURRENCY", "4"))

        if not self._api_key:
            logger.error("Missing OPENROUTER_API_KEY.")
            raise OpenRouterConfigError("Missing OPENROUTER_API_KEY")

        if OpenRouterClient._semaphore is None:
            OpenRouterClient._semaphore = asyncio.Semaphore(concurrency)
            
        if OpenRouterClient._shared_client is None:
            limits = httpx.Limits(max_keepalive_connections=concurrency, max_connections=concurrency * 2)
            OpenRouterClient._shared_client = httpx.AsyncClient(limits=limits, timeout=self._timeout)

        logger.info(f"OpenRouter client initialized. Model: {self._model}, Concurrency: {concurrency}")

    async def close(self):
        """Clean up the shared httpx client."""
        if OpenRouterClient._shared_client is not None:
            await OpenRouterClient._shared_client.aclose()
            OpenRouterClient._shared_client = None

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        
        url = f"{self._base_url}/chat/completions"
        
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": self._max_tokens
        }
        
        if self._use_json_mode and response_format and response_format.get("type") == "json_object":
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "AI Startup Validator"
        }

        base_backoff = 2.0
        start_time = time.time()

        async with OpenRouterClient._semaphore:
            for attempt in range(self._max_retries + 1):
                try:
                    req_start = time.time()
                    response = await OpenRouterClient._shared_client.post(url, headers=headers, json=payload)
                    req_duration = time.time() - req_start

                    if response.status_code == 200:
                        data = response.json()
                        choices = data.get("choices", [])
                        if not choices:
                            raise OpenRouterConfigError("No choices returned from OpenRouter.")
                        
                        content = choices[0].get("message", {}).get("content", "")
                        total_duration = time.time() - start_time
                        
                        logger.info(
                            f"OpenRouter Success | Model: {self._model} | "
                            f"Status: 200 | Latency: {req_duration:.2f}s | "
                            f"Total Time: {total_duration:.2f}s | "
                            f"Attempts: {attempt + 1}/{self._max_retries + 1} | "
                            f"Response Size: {len(content)} chars | "
                            f"Max Tokens: {self._max_tokens} | Timeout: {self._timeout}s"
                        )
                        return content

                    if response.status_code in (429, 500, 503):
                        if attempt == self._max_retries:
                            logger.error(f"Error {response.status_code} exhausted after {self._max_retries} retries.")
                            raise OpenRouterConfigError(f"API request failed with status {response.status_code}.")
                        
                        sleep_time = base_backoff * (2 ** attempt) + random.uniform(1, 3)
                        logger.warning(
                            f"OpenRouter Transient Error | Status: {response.status_code} | "
                            f"Attempt: {attempt+1} | Retrying in {sleep_time:.1f}s..."
                        )
                        await asyncio.sleep(sleep_time)
                        continue

                    logger.error(f"API request failed with status {response.status_code}: {response.text}")
                    raise OpenRouterConfigError(f"API request failed with status {response.status_code}.")

                except asyncio.CancelledError:
                    logger.warning("OpenRouter request cancelled by orchestrator. Aborting.")
                    raise
                except httpx.TimeoutException:
                    if attempt == self._max_retries:
                        logger.error(f"OpenRouter Timeout | Model: {self._model} | Timeout: {self._timeout}s | Attempt: {attempt+1}/{self._max_retries+1}")
                        raise OpenRouterConfigError(
                            f"OpenRouter Timeout\n"
                            f"Model: {self._model}\n"
                            f"Timeout: {self._timeout}s\n"
                            f"Attempt: {attempt+1}/{self._max_retries+1}"
                        )
                    sleep_time = base_backoff * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"OpenRouter Timeout | Model: {self._model} | "
                        f"Timeout: {self._timeout}s | Attempt: {attempt+1}/{self._max_retries+1} | "
                        f"Retrying in {sleep_time:.1f}s..."
                    )
                    await asyncio.sleep(sleep_time)
                except httpx.RequestError as exc:
                    if attempt == self._max_retries:
                        raise OpenRouterConfigError(f"Network error: {exc}")
                    sleep_time = base_backoff * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"OpenRouter Network Error | Attempt: {attempt+1}/{self._max_retries+1} | Retrying in {sleep_time:.1f}s...")
                    await asyncio.sleep(sleep_time)

            # Safety net: should never be reached, but prevents silent None return
            raise OpenRouterConfigError("All retry attempts exhausted without a response.")
