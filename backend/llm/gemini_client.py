import logging
import os
import random
import asyncio
import time
from typing import Any

from google import genai
from google.genai import types
from core.config import settings

logger = logging.getLogger(__name__)

class GeminiConfigError(Exception):
    pass

class GeminiClient:
    _semaphore = None
    _shared_client = None

    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or settings.llm.GOOGLE_AI_API_KEY
        self._model = model or settings.llm.GOOGLE_MODEL
        self._max_retries = settings.llm.GEMINI_MAX_RETRIES
        self._timeout = settings.llm.GEMINI_TIMEOUT
        self._max_tokens = settings.llm.GEMINI_MAX_TOKENS
        
        concurrency = settings.llm.GEMINI_CONCURRENCY

        if not self._api_key:
            logger.error("Missing GOOGLE_AI_API_KEY.")
            raise GeminiConfigError("Missing GOOGLE_AI_API_KEY")

        if GeminiClient._semaphore is None:
            GeminiClient._semaphore = asyncio.Semaphore(concurrency)
            
        if GeminiClient._shared_client is None:
            # The google-genai SDK handles its own HTTP sessions internally
            GeminiClient._shared_client = genai.Client(api_key=self._api_key)

        logger.info(f"Gemini client initialized with official SDK. Model: {self._model}, Concurrency: {concurrency}")

    async def close(self):
        """Clean up the shared client."""
        # google-genai client doesn't require explicit aclose in current versions, but we clear the reference
        GeminiClient._shared_client = None

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.2,
    ) -> str:
        
        is_json = response_format and response_format.get("type") == "json_object"
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=self._max_tokens,
            response_mime_type="application/json" if is_json else "text/plain"
        )

        base_backoff = 2.0
        start_time = time.time()

        async with GeminiClient._semaphore:
            for attempt in range(self._max_retries + 1):
                try:
                    req_start = time.time()
                    
                    # Call the official SDK async method
                    response = await asyncio.wait_for(
                        GeminiClient._shared_client.aio.models.generate_content(
                            model=self._model,
                            contents=user_prompt,
                            config=config
                        ),
                        timeout=self._timeout
                    )
                    
                    req_duration = time.time() - req_start

                    if not response.text:
                        raise GeminiConfigError("No text returned from Gemini.")
                    
                    content = response.text
                    total_duration = time.time() - start_time
                    
                    logger.info(
                        f"Gemini SDK Success | Model: {self._model} | "
                        f"Latency: {req_duration:.2f}s | "
                        f"Total Time: {total_duration:.2f}s | "
                        f"Attempts: {attempt + 1}/{self._max_retries + 1} | "
                        f"Response Size: {len(content)} chars | "
                        f"Max Tokens: {self._max_tokens} | Timeout: {self._timeout}s"
                    )
                    return content

                except asyncio.CancelledError:
                    logger.warning("Gemini request cancelled by orchestrator. Aborting.")
                    raise
                except asyncio.TimeoutError:
                    if attempt == self._max_retries:
                        logger.error(f"Gemini SDK Timeout | Model: {self._model} | Timeout: {self._timeout}s | Attempt: {attempt+1}/{self._max_retries+1}")
                        raise GeminiConfigError(
                            f"Gemini SDK Timeout\n"
                            f"Model: {self._model}\n"
                            f"Timeout: {self._timeout}s\n"
                            f"Attempt: {attempt+1}/{self._max_retries+1}"
                        )
                    sleep_time = base_backoff * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"Gemini SDK Timeout | Model: {self._model} | "
                        f"Timeout: {self._timeout}s | Attempt: {attempt+1}/{self._max_retries+1} | "
                        f"Retrying in {sleep_time:.1f}s..."
                    )
                    await asyncio.sleep(sleep_time)
                except Exception as exc:
                    # The official SDK wraps errors in various Exception classes (e.g., APIError)
                    # We catch generic exceptions to handle rate limits and transient server errors safely.
                    error_str = str(exc).lower()
                    is_quota = "quota" in error_str
                    is_transient = not is_quota and any(term in error_str for term in ["429", "500", "503", "timeout", "too many requests", "internal server error", "unavailable"])
                    
                    if is_transient and attempt < self._max_retries:
                        sleep_time = base_backoff * (2 ** attempt) + random.uniform(1, 3)
                        logger.warning(f"Gemini SDK Transient Error: {exc} | Attempt: {attempt+1}/{self._max_retries+1} | Retrying in {sleep_time:.1f}s...")
                        await asyncio.sleep(sleep_time)
                        continue
                    
                    if attempt == self._max_retries:
                        logger.error(f"Gemini SDK Error exhausted after {self._max_retries} retries: {exc}")
                        raise GeminiConfigError(f"SDK request failed: {exc}")
                    
                    # If it's a definite client error (e.g., 400 Bad Request, 404 Not Found), fail immediately
                    logger.error(f"Gemini SDK fatal error: {exc}")
                    raise GeminiConfigError(f"SDK request failed: {exc}")

            raise GeminiConfigError("All retry attempts exhausted without a response.")
