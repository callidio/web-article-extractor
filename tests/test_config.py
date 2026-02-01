"""Tests for config module."""

import pytest
from pydantic import ValidationError

from web_article_extractor.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_config_init(self):
        """Test Config initialization with pydantic."""
        config = Config(id_column="id", url_columns=["url1", "url2"])
        assert config.id_column == "id"
        assert config.url_columns == ["url1", "url2"]

    def test_config_from_yaml(self, tmp_path):
        """Test loading config from YAML."""
        yaml_content = """
id_column: rest_id
url_columns:
  - Web site restaurant
  - Web site Chef
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        config = Config.from_yaml(yaml_file)
        assert config.id_column == "rest_id"
        assert config.url_columns == ["Web site restaurant", "Web site Chef"]

    def test_config_from_yaml_missing_file(self):
        """Test error when YAML file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("nonexistent.yaml")

    def test_config_from_yaml_missing_id_column(self, tmp_path):
        """Test error when id_column is missing."""
        yaml_content = """
url_columns:
  - url1
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        with pytest.raises(ValidationError):
            Config.from_yaml(yaml_file)

    def test_config_from_yaml_missing_url_columns(self, tmp_path):
        """Test error when url_columns is missing."""
        yaml_content = """
id_column: id
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        with pytest.raises(ValidationError):
            Config.from_yaml(yaml_file)

    def test_config_from_yaml_empty_url_columns(self, tmp_path):
        """Test error when url_columns is empty."""
        yaml_content = """
id_column: id
url_columns: []
"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        with pytest.raises(ValidationError, match="url_columns must not be empty"):
            Config.from_yaml(yaml_file)

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(id_column="id", url_columns=["url1", "url2"])
        result = config.to_dict()
        assert result == {"id_column": "id", "url_columns": ["url1", "url2"]}

    def test_config_from_yaml_invalid_dict(self, tmp_path):
        """Test error when YAML is not a dictionary."""
        yaml_content = "- item1\n- item2"
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml_content)

        with pytest.raises(ValueError, match="YAML file must contain a dictionary"):
            Config.from_yaml(yaml_file)
