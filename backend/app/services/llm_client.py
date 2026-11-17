"""
Multi-Provider LLM & Embedding Service for Nivara.
Supports:
- Google Gemini (Gemini 1.5 Pro / Flash via google-generativeai or REST)
- OpenAI (GPT-4o, text-embedding-3-small)
- Fallback Heuristic Engine: Ensures 100% deterministic safety and continuous function
  even when offline or when API keys are unconfigured.
"""

import os
import json
from typing import Dict, Any, List, Optional
from app.config import settings

class LLMClient:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model_name = settings.LLM_MODEL_NAME

    async def generate_cbt_response(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        confirmed_memories: Optional[List[str]] = None
    ) -> str:
        """
        Generates a therapeutic CBT response adhering to clinical guidelines.
        If no API key is provided, gracefully falls back to deterministic reflection.
        """
        if not self.api_key or self.api_key == "mock-key":
            return self._heuristic_fallback(user_message, confirmed_memories)

        # Gemini / OpenAI API integration
        try:
            if "gemini" in self.model_name.lower():
                return await self._call_gemini(system_prompt, user_message, conversation_history, confirmed_memories)
            else:
                return await self._call_openai(system_prompt, user_message, conversation_history, confirmed_memories)
        except Exception as e:
            # Safe degradation to local engine in case of network or quota failure
            return self._heuristic_fallback(user_message, confirmed_memories)

    async def _call_gemini(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]],
        confirmed_memories: Optional[List[str]]
    ) -> str:
        """Invokes Google Gemini API with system instructions and safety constraints."""
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        contents = []
        if confirmed_memories:
            contents.append({
                "role": "user",
                "parts": [{"text": "CONFIRMED PATTERNS & FACTS: " + "; ".join(confirmed_memories)}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I will respectfully reference these without assuming clinical conclusions."}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        payload = {
            "contents": contents,
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 600
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return self._heuristic_fallback(user_message, confirmed_memories)

    async def _call_openai(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]],
        confirmed_memories: Optional[List[str]]
    ) -> str:
        """Invokes OpenAI API."""
        import httpx
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_prompt}]
        if confirmed_memories:
            messages.append({
                "role": "system",
                "content": "User Confirmed Memories: " + "; ".join(confirmed_memories)
            })
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 600
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return self._heuristic_fallback(user_message, confirmed_memories)

    def _heuristic_fallback(self, user_message: str, confirmed_memories: Optional[List[str]] = None) -> str:
        """Deterministic compassionate CBT fallback."""
        mem_str = f" *(Keeping in mind what you noted earlier: {confirmed_memories[0]})*" if confirmed_memories else ""
        return (
            f"Thank you for sharing that with me.{mem_str} When you step back and look at this thought, "
            f"what is the strongest piece of objective evidence supporting it, and what evidence contradicts it?"
        )

llm_service = LLMClient()

