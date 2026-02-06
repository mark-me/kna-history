"""
KNA Data CLI

Command-line interface for data loading operations.
"""
import argparse
import sys

from .loader import KnaDataLoader
from .config import get_config
from logging_kna import logger


def load_command(args):
    """Handle the load command.

    Runs optional validation and then loads data from the given Excel file into the configured database.
    """
    env = "development" if args.dev else "production"
    config = get_config(env)
    loader = KnaDataLoader(config=config)

    logger.info(f"Loading data from: {args.file}")
    logger.info(f"Using environment: {env}")
    logger.info(f"Database host: {config.MARIADB_HOST}")

    if not args.skip_validation:
        _validate_load_file(loader=loader, args=args)

    _execute_load(loader=loader, args=args)


def _validate_load_file(loader: KnaDataLoader, args) -> None:
    """Validate the Excel file before loading.

    Runs validation on the provided Excel file and stops the load when blocking errors are found, 
    while still reporting non-fatal warnings.
    """
    logger.info("Validating Excel file...")
    validation = loader.validate_excel(args.file)

    if not validation["valid"]:
        logger.error("Validation failed!")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
        sys.exit(1)

    logger.info("Validation passed!")
    logger.info(f"Found sheets: {validation['info']}")

    if validation["warnings"]:
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")


def _execute_load(loader: KnaDataLoader, args) -> None:
    """Run the actual Excel load and handle errors.

    Executes the data load from the provided Excel file, logs a summary of loaded rows per table, 
    and handles failures based on verbosity settings.

    Args:
        loader (KnaDataLoader): Loader instance responsible for importing the Excel data.
        args: Parsed CLI arguments containing the file path and verbosity options.
    """
    try:
        stats = loader.load_from_excel(args.file)
        logger.info("=" * 50)
        logger.info("Load completed successfully!")
        logger.info("=" * 50)
        for table, count in stats.items():
            logger.info(f"{table:20s}: {count:>6} rows")
    except Exception as e:
        logger.error(f"Load failed: {e}")
        if args.verbose:
            raise
        sys.exit(1)


def validate_command(args):
    """Handle the validate command.

    Runs validation for the provided Excel file and logs the outcome without modifying any data.
    """
    env = "development" if args.dev else "production"
    config = get_config(env)
    loader = KnaDataLoader(config=config)

    logger.info(f"Validating: {args.file}")
    validation = loader.validate_excel(args.file)

    if validation["valid"]:
        _log_validation_success(validation)
    else:
        _log_validation_failure_and_exit(validation)


def _log_validation_success(validation: dict) -> None:
    """Log details when validation passes.

    Outputs summary information about validated sheets and any non-fatal warnings discovered 
    during validation.

    Args:
        validation (dict): Validation result containing sheet info and optional warnings.
    """
    logger.info("✅ Validation PASSED")
    logger.info("Sheet information:")
    for sheet, count in validation["info"].items():
        logger.info(f"  {sheet:20s}: {count:>6} rows")

    if validation["warnings"]:
        logger.warning("Warnings:")
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")


def _log_validation_failure_and_exit(validation: dict) -> None:
    """Log details when validation fails and exit."""
    logger.error("❌ Validation FAILED")
    for error in validation["errors"]:
        logger.error(f"  - {error}")
    sys.exit(1)


def thumbnails_command(args):
    """Handle the thumbnails command"""
    env = "development" if args.dev else "production"
    config = get_config(env)
    loader = KnaDataLoader(config=config)

    logger.info("Generating thumbnails...")
    count = loader._generate_thumbnails()
    logger.info(f"✅ Generated {count} thumbnails")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="KNA Data Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate Excel file
  python -m kna_data.cli validate /path/to/kna_database.xlsx

  # Load data from Excel (production database)
  python -m kna_data.cli load /path/to/kna_database.xlsx

  # Load data (development database)
  python -m kna_data.cli load --dev /path/to/kna_database.xlsx

  # Load without validation
  python -m kna_data.cli load --skip-validation /path/to/kna_database.xlsx

  # Generate thumbnails only
  python -m kna_data.cli thumbnails
        """
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Use development database (localhost:3306) instead of production"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed error messages"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Load command
    load_parser = subparsers.add_parser("load", help="Load data from Excel file")
    load_parser.add_argument("file", help="Path to Excel file")
    load_parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation before loading"
    )
    load_parser.set_defaults(func=load_command)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate Excel file")
    validate_parser.add_argument("file", help="Path to Excel file")
    validate_parser.set_defaults(func=validate_command)

    # Thumbnails command
    thumbnails_parser = subparsers.add_parser("thumbnails", help="Generate thumbnails")
    thumbnails_parser.set_defaults(func=thumbnails_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
