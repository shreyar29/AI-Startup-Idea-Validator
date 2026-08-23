import re
import logging
from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security import APIKeyHeader
from core.config import settings

logger = logging.getLogger("security")

# Security headers configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class SecurityManager:
    """
    Centralized Security Manager handling API abuse protection, 
    prompt injection sanitization, and request validation.
    """
    
    # Advanced Heuristic Prompt Injection Patterns
    INJECTION_PATTERNS = [
        r"(?i)\bignore\b.*\bprevious\b.*\binstructions\b",
        r"(?i)\bignore\b.*\bcontext\b",
        r"(?i)\bsystem\s+prompt\b",
        r"(?i)\bforget\b.*\beverything\b",
        r"(?i)you\s+are\s+now\b",
        r"(?i)\bjailbreak\b",
        r"(?i)bypass\s+restrictions",
        r"(?i)\bprint\b.*\binstructions\b",
        r"(?i)\bprint\b.*\bprompt\b",
        r"(?i)\bnew\s+role\b",
        r"(?i)act\s+as\s+an\s+uncensored",
        r"(?i)base64", 
        r"(?i)hex\s+decode",
        r"<script.*?>",
        r"(?i)\bdrop\s+table\b",
        r"(?i)\bdelete\s+from\b"
    ]
    
    COMPILED_PATTERNS = [re.compile(p) for p in INJECTION_PATTERNS]

    @classmethod
    def validate_api_key(cls, api_key: Optional[str] = None) -> bool:
        """Validates the incoming API key against the server secret."""
        # For MVP phase, if SECRET_KEY is not strictly enforced in dev, allow pass.
        # In production, this must match settings.app.SECRET_KEY.
        expected_key = settings.app.SECRET_KEY
        if not expected_key or expected_key == "changeme":
            return True
        if not api_key or api_key != expected_key:
            logger.warning("Unauthorized API access attempt.")
            return False
        return True

    @classmethod
    def sanitize_prompt(cls, user_input: str) -> str:
        """
        Calculates a heuristic threat score for the prompt.
        If the score exceeds the threshold, blocks the request.
        """
        if not user_input or not user_input.strip():
            raise ValueError("Input cannot be empty.")
            
        clean_input = user_input.strip()
        threat_score = 0
        
        # 1. Length bounds (Prevent buffer overflow / context exhaustion)
        if len(clean_input) > 20000:
            logger.warning(f"Prompt length exceeded: {len(clean_input)} chars.")
            raise ValueError("Input exceeds maximum allowed length.")
            
        # 2. Heuristic Pattern Matching
        for pattern in cls.COMPILED_PATTERNS:
            if pattern.search(clean_input):
                threat_score += 10
                
        # 3. Structural Anomalies
        # Unusually high number of special characters (obfuscation attempt)
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', clean_input)) / max(len(clean_input), 1)
        if special_char_ratio > 0.3:
            threat_score += 5
            
        # Many repeated characters
        if re.search(r'(.)\1{20,}', clean_input):
            threat_score += 5

        # Decision
        if threat_score >= 10:
            logger.error(f"Prompt Injection Detected! Threat Score: {threat_score}. Input Snippet: {clean_input[:50]}")
            raise HTTPException(
                status_code=400, 
                detail="Security Guardrail Triggered: Disallowed patterns detected in the input."
            )
            
        return clean_input
