"""Google Gemini API Provider implementation."""

import google.generativeai as genai

from .base import BaseAPIProvider


class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors."""


class GeminiAPI(BaseAPIProvider):
    """Google Gemini API provider."""

    def get_env_key_name(self) -> str:
        """Return environment variable name for Gemini API key."""
        return "GEMINI_API_KEY"

    def _initialize_client(self):
        """Initialize Gemini client."""
        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel(self.model)

    def get_default_model(self) -> str:
        """Return default Gemini model."""
        return "gemini-2.0-flash-exp"

    def query(self, prompt: str) -> str:
        """
        Query Gemini API.

        Args:
            prompt: The prompt text

        Returns:
            Response text from Gemini

        Raises:
            Exception: If Gemini API call fails
        """
        try:
            generation_config = {
                "temperature": 0,
                "max_output_tokens": 8096,
            }

            response = self.client.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            raise GeminiAPIError(f"Gemini API error: {e}") from e
