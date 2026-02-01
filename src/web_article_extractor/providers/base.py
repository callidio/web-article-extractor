"""Base API Provider abstract class."""

import os
from abc import ABC, abstractmethod


class BaseAPIProvider(ABC):
    """Abstract base class for API providers."""

    def __init__(self, model: str = None):
        """
        Initialize API provider.

        Args:
            model: Model name to use. If None, uses default model.
        """
        self.model = model or self.get_default_model()
        self.api_key = self._get_api_key()
        self.client = self._initialize_client()

    def _get_api_key(self) -> str:
        """
        Get API key from environment variable.

        Returns:
            API key string

        Raises:
            ValueError: If API key is not found
        """
        env_key = self.get_env_key_name()
        api_key = os.getenv(env_key)
        if not api_key:
            raise ValueError(f"API key not found. Please set {env_key} environment variable.")
        return api_key

    @abstractmethod
    def get_env_key_name(self) -> str:
        """
        Return environment variable name for API key.

        Returns:
            Environment variable name
        """

    @abstractmethod
    def _initialize_client(self):
        """
        Initialize API client.

        Returns:
            Initialized client object
        """

    @abstractmethod
    def get_default_model(self) -> str:
        """
        Return default model name.

        Returns:
            Default model name
        """

    @abstractmethod
    def query(self, prompt: str) -> str:
        """
        Query the API with a prompt.

        Args:
            prompt: The prompt text

        Returns:
            Response text from API

        Raises:
            Exception: If API call fails
        """
