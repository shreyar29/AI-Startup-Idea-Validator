import logging
import random
import asyncio
import time
from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import APIError
from core.config import settings

logger = logging.getLogger(__name__)

class GeminiConfigError(Exception):
    pass

class GeminiClient:
    _semaphore = None
    _shared_client = None
    _init_lock = asyncio.Lock()
    
    # Circuit Breaker & Metrics State
    _consecutive_failures = 0
    _circuit_breaker_cooldown_until = 0
    _MAX_FAILURES = 5
    _COOLDOWN_SECONDS = 30
    
    _metrics = {
        "success_count": 0,
        "timeout_count": 0,
        "retry_count": 0,
        "quota_failures": 0,
        "circuit_breaker_trips": 0
    }

    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or settings.llm.GOOGLE_AI_API_KEY
        self._model = model or settings.llm.GOOGLE_MODEL
        self._max_retries = settings.llm.GEMINI_MAX_RETRIES
        self._timeout = settings.llm.GEMINI_TIMEOUT
        self._max_tokens = settings.llm.GEMINI_MAX_TOKENS
        
        self._concurrency = settings.llm.GEMINI_CONCURRENCY

        if not self._api_key:
            logger.error("Missing GOOGLE_AI_API_KEY.")
            raise GeminiConfigError("Missing GOOGLE_AI_API_KEY")

    async def _ensure_initialized(self):
        if GeminiClient._semaphore is None:
            GeminiClient._semaphore = asyncio.Semaphore(self._concurrency)
            
        if GeminiClient._shared_client is None:
            async with GeminiClient._init_lock:
                if GeminiClient._shared_client is None:
                    # The google-genai SDK handles its own HTTP sessions internally
                    GeminiClient._shared_client = genai.Client(api_key=self._api_key)
                    logger.info(f"Gemini client securely initialized. Model: {self._model}, Concurrency: {self._concurrency}")

    async def close(self):
        """Clean up the shared client."""
        async with GeminiClient._init_lock:
            GeminiClient._shared_client = None

    def _check_circuit_breaker(self):
        if time.time() < GeminiClient._circuit_breaker_cooldown_until:
            raise GeminiConfigError("Circuit breaker is currently open. Provider is degraded.")
            
        # Half-open: if time is past, we let requests through.
        # If they fail again, consecutive failures will immediately trip it back open.

    def _trip_circuit_breaker(self):
        GeminiClient._metrics["circuit_breaker_trips"] += 1
        GeminiClient._circuit_breaker_cooldown_until = time.time() + GeminiClient._COOLDOWN_SECONDS
        logger.error(f"Circuit breaker tripped! Pausing outbound requests for {GeminiClient._COOLDOWN_SECONDS}s.")

    def _handle_failure(self):
        GeminiClient._consecutive_failures += 1
        if GeminiClient._consecutive_failures >= GeminiClient._MAX_FAILURES:
            self._trip_circuit_breaker()

    def _handle_success(self):
        GeminiClient._consecutive_failures = 0
        GeminiClient._metrics["success_count"] += 1

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
        temperature: float = 0.2,
    ) -> str:
        await self._ensure_initialized()
        self._check_circuit_breaker()
        
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
                        self._handle_failure()
                        raise GeminiConfigError("Provider returned an empty completion.")
                    
                    self._handle_success()
                    
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
                    GeminiClient._metrics["timeout_count"] += 1
                    if attempt == self._max_retries:
                        self._handle_failure()
                        logger.error(f"Gemini SDK Timeout | Model: {self._model} | Timeout: {self._timeout}s | Attempt: {attempt+1}/{self._max_retries+1}")
                        raise GeminiConfigError("Provider timed out after maximum retry attempts.")
                    
                    GeminiClient._metrics["retry_count"] += 1
                    sleep_time = base_backoff * (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"Gemini SDK Timeout | Model: {self._model} | "
                        f"Timeout: {self._timeout}s | Attempt: {attempt+1}/{self._max_retries+1} | "
                        f"Retrying in {sleep_time:.1f}s..."
                    )
                    await asyncio.sleep(sleep_time)
                except APIError as exc:
                    # Prefer native SDK error handling
                    status_code = getattr(exc, 'code', 500)
                    is_quota = status_code == 429
                    is_transient = status_code in [429, 500, 502, 503, 504]
                    
                    if is_quota:
                        GeminiClient._metrics["quota_failures"] += 1
                        
                    if is_transient and attempt < self._max_retries:
                        GeminiClient._metrics["retry_count"] += 1
                        sleep_time = base_backoff * (2 ** attempt) + random.uniform(1, 3)
                        logger.warning(f"Gemini API Transient Error (HTTP {status_code}) | Attempt: {attempt+1}/{self._max_retries+1} | Retrying in {sleep_time:.1f}s...")
                        await asyncio.sleep(sleep_time)
                        continue
                    
                    self._handle_failure()
                    logger.error(f"Gemini SDK fatal error (HTTP {status_code}).")
                    raise GeminiConfigError(f"Provider request failed (HTTP {status_code}).")
                except Exception as exc:
                    # Fallback string matching for untyped low-level transport errors
                    error_str = str(exc).lower()
                    is_quota = "quota" in error_str or "429" in error_str
                    is_transient = not is_quota and any(term in error_str for term in ["429", "500", "503", "timeout", "too many requests", "internal server error", "unavailable", "connection reset"])
                    
                    if is_quota:
                        GeminiClient._metrics["quota_failures"] += 1
                        
                    if is_transient and attempt < self._max_retries:
                        GeminiClient._metrics["retry_count"] += 1
                        sleep_time = base_backoff * (2 ** attempt) + random.uniform(1, 3)
                        logger.warning(f"Gemini Transport Error (Transient) | Attempt: {attempt+1}/{self._max_retries+1} | Retrying in {sleep_time:.1f}s...")
                        await asyncio.sleep(sleep_time)
                        continue
                    
                    self._handle_failure()
                    logger.error(f"Gemini transport fatal error: {type(exc).__name__}")
                    raise GeminiConfigError(f"Provider transport failed with {type(exc).__name__}.")

            self._handle_failure()
            raise GeminiConfigError("All retry attempts exhausted without a response.")
            
    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ):
        await self._ensure_initialized()
        self._check_circuit_breaker()
        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=self._max_tokens,
            response_mime_type="text/plain"
        )
        
        async with GeminiClient._semaphore:
            try:
                response_stream = await GeminiClient._shared_client.aio.models.generate_content_stream(
                    model=self._model,
                    contents=user_prompt,
                    config=config
                )
                async for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                self._handle_success()
            except Exception as e:
                self._handle_failure()
                logger.error(f"Streaming failed with error: {type(e).__name__}")
                raise GeminiConfigError(f"Streaming failed due to provider error.")
