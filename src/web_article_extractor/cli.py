"""Command-line interface for web article extractor."""

from pathlib import Path

import click
from dotenv import load_dotenv

from .config import Config
from .extractor import ArticleExtractor
from .logger import setup_logger

# Load environment variables from .env file
load_dotenv()


@click.command()
@click.argument("input_csv", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-csv",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Path to output CSV file for results",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to YAML configuration file specifying column mappings",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Set logging level",
)
def main(input_csv: Path, output_csv: Path, config: Path, log_level: str) -> None:
    """
    Extract article text and dates from URLs in CSV file.

    INPUT_CSV: Path to input CSV file containing URLs
    """
    # Setup logging
    setup_logger("web_article_extractor", log_level)

    try:
        # Load configuration
        cfg = Config.from_yaml(config)

        # Initialize extractor
        extractor = ArticleExtractor()

        # Process CSV
        extractor.process_csv(input_csv, output_csv, cfg)

        click.echo(f"✓ Extraction complete. Results saved to {output_csv}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
