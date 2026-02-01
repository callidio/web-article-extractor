"""Tests for CLI module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from web_article_extractor.cli import main


class TestCLI:
    """Tests for command-line interface."""

    def test_cli_missing_output_option(self, tmp_path):
        """Test CLI error when output option is missing."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text("id_column: id\nurl_columns:\n  - url")

        runner = CliRunner()
        result = runner.invoke(main, [str(input_csv)])

        assert result.exit_code != 0

    def test_cli_missing_config_option(self, tmp_path):
        """Test CLI error when config option is missing."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        output_csv = tmp_path / "output.csv"

        runner = CliRunner()
        result = runner.invoke(main, [str(input_csv), "--output-csv", str(output_csv)])

        assert result.exit_code != 0

    def test_cli_with_short_options(self, tmp_path):
        """Test CLI with short option flags."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        output_csv = tmp_path / "output.csv"
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text("id_column: id\nurl_columns:\n  - url")

        runner = CliRunner()
        
        with patch("web_article_extractor.cli.ArticleExtractor") as mock_extractor:
            mock_instance = Mock()
            mock_extractor.return_value = mock_instance
            
            result = runner.invoke(
                main, [str(input_csv), "-o", str(output_csv), "-c", str(config_yaml)]
            )

            assert result.exit_code == 0
            assert "Extraction complete" in result.output

    def test_cli_with_long_options(self, tmp_path):
        """Test CLI with long option flags."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        output_csv = tmp_path / "output.csv"
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text("id_column: id\nurl_columns:\n  - url")

        runner = CliRunner()
        
        with patch("web_article_extractor.cli.ArticleExtractor") as mock_extractor:
            mock_instance = Mock()
            mock_extractor.return_value = mock_instance
            
            result = runner.invoke(
                main,
                [str(input_csv), "--output-csv", str(output_csv), "--config", str(config_yaml)],
            )

            assert result.exit_code == 0

    def test_cli_with_log_level(self, tmp_path):
        """Test CLI with log level option."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        output_csv = tmp_path / "output.csv"
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text("id_column: id\nurl_columns:\n  - url")

        runner = CliRunner()
        
        with patch("web_article_extractor.cli.ArticleExtractor") as mock_extractor:
            with patch("web_article_extractor.cli.setup_logger") as mock_logger:
                mock_instance = Mock()
                mock_extractor.return_value = mock_instance
                
                result = runner.invoke(
                    main,
                    [
                        str(input_csv),
                        "-o",
                        str(output_csv),
                        "-c",
                        str(config_yaml),
                        "--log-level",
                        "DEBUG",
                    ],
                )

                assert result.exit_code == 0
                mock_logger.assert_called_once_with("web_article_extractor", "DEBUG")

    def test_cli_invalid_log_level(self, tmp_path):
        """Test CLI with invalid log level."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        output_csv = tmp_path / "output.csv"
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text("id_column: id\nurl_columns:\n  - url")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [str(input_csv), "-o", str(output_csv), "-c", str(config_yaml), "--log-level", "INVALID"],
        )

        assert result.exit_code != 0

    def test_cli_nonexistent_input(self, tmp_path):
        """Test CLI with nonexistent input file."""
        output_csv = tmp_path / "output.csv"
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text("id_column: id\nurl_columns:\n  - url")

        runner = CliRunner()
        result = runner.invoke(
            main, ["nonexistent.csv", "-o", str(output_csv), "-c", str(config_yaml)]
        )

        assert result.exit_code != 0

    def test_cli_nonexistent_config(self, tmp_path):
        """Test CLI with nonexistent config file."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        output_csv = tmp_path / "output.csv"

        runner = CliRunner()
        result = runner.invoke(
            main, [str(input_csv), "-o", str(output_csv), "-c", "nonexistent.yaml"]
        )

        assert result.exit_code != 0

    def test_cli_exception_handling(self, tmp_path):
        """Test CLI handles exceptions gracefully."""
        input_csv = tmp_path / "input.csv"
        input_csv.write_text("id,url\n1,https://example.com")
        output_csv = tmp_path / "output.csv"
        config_yaml = tmp_path / "config.yaml"
        config_yaml.write_text("id_column: id\nurl_columns:\n  - url")

        runner = CliRunner()
        
        with patch("web_article_extractor.cli.Config.from_yaml") as mock_config:
            mock_config.side_effect = Exception("Config error")
            
            result = runner.invoke(
                main, [str(input_csv), "-o", str(output_csv), "-c", str(config_yaml)]
            )

            assert result.exit_code != 0
            assert "Error" in result.output
