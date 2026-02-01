"""Tests for providers module."""

import os
from unittest.mock import Mock, patch

import pytest

from web_article_extractor.providers.gemini import GeminiAPI


class TestGeminiAPI:
    """Tests for GeminiAPI class."""

    def test_gemini_api_get_env_key_name(self):
        """Test getting environment variable name."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            api = GeminiAPI()
            assert api.get_env_key_name() == "GEMINI_API_KEY"

    def test_gemini_api_get_default_model(self):
        """Test getting default model name."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            api = GeminiAPI()
            assert api.get_default_model() == "gemini-2.0-flash-exp"

    def test_gemini_api_missing_key(self):
        """Test error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key not found"):
                GeminiAPI()

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_gemini_api_query(self, mock_model_class, mock_configure):  # pylint: disable=unused-argument
        """Test querying Gemini API."""
        # Setup mocks
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            api = GeminiAPI()
            result = api.query("test prompt")

            assert result == "Test response"
            mock_model.generate_content.assert_called_once()

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_gemini_api_query_error(
        self, mock_model_class, mock_configure
    ):  # pylint: disable=unused-argument
        """Test error handling in Gemini query."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            api = GeminiAPI()
            with pytest.raises(Exception, match="Gemini API error"):
                api.query("test prompt")

    @patch("google.generativeai.configure")
    @patch("google.generativeai.GenerativeModel")
    def test_gemini_api_custom_model(
        self, mock_model_class, mock_configure
    ):  # pylint: disable=unused-argument
        """Test using custom model."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            api = GeminiAPI(model="gemini-1.5-pro")
            assert api.model == "gemini-1.5-pro"
