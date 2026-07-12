"""
openrouter_client.py

Purpose
-------
This module provides a reusable, agent-agnostic client for communicating
with the OpenRouter API. It knows nothing about startup ideas, search
queries, market analysis, or Tavily — its only job is: given a system
prompt and a user prompt, send them to the configured model on OpenRouter
and return the generated text.

Any current or future agent in the Multi-Agent System (Query Strategist,
Market Analysis Agent, SWOT Agent, etc.) can depend on this same client
without coupling to each other's business logic.

This module contains NO business logic, NO prompt content, and NO
knowledge of any specific agent's responsibilities.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables from .env as early as possible so that
# configuration is available the moment this module is imported.
load_dotenv()

logger = logging.getLogger(__name__)


# ============================================================
# CUSTOM EXCEPTIONS
# ============================================================
# Domain-specific exceptions let callers (e.g., query_strategist.py) catch
# LLM-client failures without needing to know about httpx internals.

class OpenRouterConfigError(Exception):
    """Raised when required configuration (env vars) is missing or invalid."""


class OpenRouterAuthError(Exception):
    """Raised when the OpenRouter API rejects the request due to an invalid
    or missing API key."""


class OpenRouterTimeoutError(Exception):
    """Raised when a request to OpenRouter times out."""


class OpenRouterNetworkError(Exception):
    """Raised when a network-level failure prevents reaching OpenRouter."""


class OpenRouterAPIError(Exception):
    """Raised when OpenRouter responds with a non-success status code that
    is not specifically an authentication failure."""


class OpenRouterResponseError(Exception):
    """Raised when OpenRouter's response body is missing expected fields or
    cannot be parsed into a usable response."""


# ============================================================
# CLIENT
# ============================================================

class OpenRouterClient:
    """
    A minimal, reusable async client for the OpenRouter chat completions
    API. Any agent that needs to call an LLM can construct one of these
    and call `generate_response()`.

    This class deliberately has no awareness of what the prompts contain
    or what the response will be used for — that separation keeps it
    reusable across every current and future agent in the system.
    """

    # Default timeout (seconds) applied to every request unless overridden.
    DEFAULT_TIMEOUT_SECONDS: float = 30.0

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        """
        Initialize the OpenRouter client.

        Configuration values fall back to environment variables when not
        explicitly passed in, so the client can be constructed with zero
        arguments in normal application use, while still being easy to
        override for testing.

        Args:
            api_key: OpenRouter API key. Falls back to OPENROUTER_API_KEY.
            model: Model identifier to use. Falls back to OPENROUTER_MODEL.
            base_url: OpenRouter API base URL. Falls back to
                OPENROUTER_BASE_URL.
            timeout_seconds: Per-request timeout. Defaults to
                DEFAULT_TIMEOUT_SECONDS if not provided.

        Raises:
            OpenRouterConfigError: If any required configuration value is
                missing after checking both the constructor argument and
                the corresponding environment variable.
        """
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self._model = model or os.getenv("OPENROUTER_MODEL")
        self._base_url = base_url or os.getenv("OPENROUTER_BASE_URL")
        self._timeout_seconds = timeout_seconds or self.DEFAULT_TIMEOUT_SECONDS

        self._validate_config()

        logger.info("OpenRouter client initialized.")

    def _validate_config(self) -> None:
        """
        Ensure all required configuration values are present. Fails fast at
        construction time rather than at the moment of the first request.
        """
        missing = [
            name
            for name, value in (
                ("OPENROUTER_API_KEY", self._api_key),
                ("OPENROUTER_MODEL", self._model),
                ("OPENROUTER_BASE_URL", self._base_url),
            )
            if not value
        ]
        if missing:
            message = (
                f"Missing required OpenRouter configuration: {missing}. "
                f"Set these in your .env file or pass them explicitly."
            )
            logger.error(message)
            raise OpenRouterConfigError(message)

    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        """
        Send a system prompt and user prompt to OpenRouter and return the
        generated assistant text.

        Args:
            system_prompt: The system-level instructions for the model.
            user_prompt: The user-level input for the model.
            response_format: Optional dict to request structured output, e.g., {"type": "json_object"}.

        Returns:
            The generated response text from the assistant.

        Raises:
            OpenRouterAuthError: If the API key is invalid or rejected.
            OpenRouterTimeoutError: If the request times out.
            OpenRouterNetworkError: If a network-level error occurs.
            OpenRouterAPIError: For other non-success HTTP responses.
            OpenRouterResponseError: If the response body is malformed or
                missing expected fields.
        """
        payload = self._build_payload(system_prompt, user_prompt, response_format)
        headers = self._build_headers()

        logger.info("Sending request to OpenRouter (model=%s).", self._model)

        raw_response = await self._send_request(headers, payload)
        response_text = self._parse_response(raw_response)

        logger.info("Response received successfully from OpenRouter.")
        return response_text

    def _build_payload(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build the JSON request body for the chat completions endpoint."""
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if response_format:
            payload["response_format"] = response_format
        return payload

    def _build_headers(self) -> dict[str, str]:
        """Build request headers, including the bearer token."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def _send_request(
        self,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Perform the actual HTTP call to OpenRouter and return the parsed
        JSON body on success. All failure modes are translated into the
        module's custom exception types.
        """
        url = f"{self._base_url.rstrip('/')}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            logger.error("Timeout occurred while calling OpenRouter.")
            raise OpenRouterTimeoutError(
                "Request to OpenRouter timed out."
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Network error while calling OpenRouter: %s", exc)
            raise OpenRouterNetworkError(
                "A network error occurred while contacting OpenRouter."
            ) from exc

        if response.status_code == 401:
            logger.error("Invalid API Key rejected by OpenRouter.")
            raise OpenRouterAuthError(
                "OpenRouter rejected the request due to an invalid API key."
            )

        if response.status_code >= 400:
            logger.error(
                "API request failed with status %s: %s",
                response.status_code,
                response.text,
            )
            raise OpenRouterAPIError(
                f"OpenRouter API request failed with status "
                f"{response.status_code}."
            )

        try:
            return response.json()
        except ValueError as exc:
            logger.error("Failed to decode JSON from OpenRouter response.")
            raise OpenRouterResponseError(
                "OpenRouter response body was not valid JSON."
            ) from exc

    def _parse_response(self, raw_response: dict[str, Any]) -> str:
        """
        Extract the assistant's generated text from OpenRouter's response
        body, validating that the expected structure is present.
        """
        try:
            choices = raw_response["choices"]
            content = choices[0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            logger.error(
                "Unexpected response structure from OpenRouter: %s",
                raw_response,
            )
            raise OpenRouterResponseError(
                "OpenRouter response did not contain the expected "
                "'choices[0].message.content' structure."
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise OpenRouterResponseError(
                "OpenRouter response content was empty."
            )

        return content


# ============================================================
# MANUAL / STANDALONE TEST ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    async def _main() -> None:
        try:
            client = OpenRouterClient()
            result = await client.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say Hello",
            )
            print("Response from OpenRouter:")
            print(result)
        except (
            OpenRouterConfigError,
            OpenRouterAuthError,
            OpenRouterTimeoutError,
            OpenRouterNetworkError,
            OpenRouterAPIError,
            OpenRouterResponseError,
        ) as known_error:
            logger.error("Client test run failed: %s", known_error)
        except Exception:
            logger.exception("Unexpected exception during client test run.")

    asyncio.run(_main())
