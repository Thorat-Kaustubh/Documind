import os
import json
import logging
from typing import Optional
from groq import Groq
from .configuration import config

logger = logging.getLogger(__name__)

class SemanticCompressor:
    """
    Semantic Data Compressor using Groq Llama 3.1 8B.
    Acts as a 'token-saving shield' for core reasoning models.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found. Compression will fallback to truncation.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
        
        self.model = config.fast_model
        self.input_cap = 8000
        self.fallback_cap = 2000
        self.threshold = 300

    def compress(self, text: str) -> str:
        """
        Compresses input text using semantic extraction.
        
        Rules:
        - If text < 300 chars, return as is.
        - Cap input at 8,000 characters.
        - Instruct LLM to extract critical facts/technical data, remove fluff/narrative.
        - Output dense bullet points.
        - Fallback to hard truncation (2,000 chars) on failure.
        """
        if not text or len(text) <= self.threshold:
            return text

        # Input Cap
        raw_input = text[:self.input_cap]
        
        if not self.client:
            return raw_input[:self.fallback_cap]

        prompt = self._get_prompt(raw_input)

        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional synthesis engine. Output dense facts only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1, # Keep it deterministic
                max_tokens=1000  # Compressed output should be relatively short
            )
            compressed_text = chat_completion.choices[0].message.content.strip()
            
            if not compressed_text:
                raise ValueError("Empty response from compression model")
                
            return compressed_text
            
        except Exception as e:
            logger.error(f"Semantic compression failed: {e}. Falling back to hard truncation.")
            return raw_input[:self.fallback_cap]

    async def compress_async(self, text: str) -> str:
        """
        Asynchronous version of the semantic compressor.
        Uses asyncio.to_thread for the synchronous Groq client call.
        """
        import asyncio
        if not text or len(text) <= self.threshold:
            return text
            
        if not self.client:
            return text[:self.fallback_cap]

        return await asyncio.to_thread(self.compress, text)

    def _get_prompt(self, input_text: str) -> str:
        return (
            "You are a high-density semantic data compressor. "
            "Identify and extract ONLY critical facts, technical data, and key metrics. "
            "Remove all narrative fluff, repetitive headers, conversational filler, and meta-commentary. "
            "Output the result as dense bullet points for maximum information density. "
            "Do not include any introductory or concluding remarks.\n\n"
            f"INPUT TEXT:\n{input_text}"
        )

# Singleton instance for easy access
compressor = SemanticCompressor()
