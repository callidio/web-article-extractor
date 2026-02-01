"""Configuration loader for web article extractor."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Configuration container for CSV column mappings."""

    id_column: str = Field(..., description="Name of the column containing unique identifiers")
    url_columns: list[str] = Field(..., description="List of column names containing URLs to extract")
    skip_domains: list[str] = Field(
        default_factory=list, description="List of domains to skip (e.g., instagram.com, nytimes.com)"
    )

    @field_validator("url_columns")
    @classmethod
    def validate_url_columns(cls, v: list[str]) -> list[str]:
        """Validate url_columns is not empty."""
        if not v:
            raise ValueError("url_columns must not be empty")
        return v

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "Config":
        """
        Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            Config instance

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If required fields are missing or invalid
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError("YAML file must contain a dictionary")

        return cls(**data)

    def to_dict(self) -> dict[str, str | list[str]]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {"id_column": self.id_column, "url_columns": self.url_columns}
