"""
KNA Data CLI

Command-line interface for data loading operations.
"""
import argparse
import sys
from pathlib import Path

from .config import Config
from .loader import KnaDataLoader
from logging_kna import logger


def load_command(args):
    """Handle the load command"""
    config = Config.for_development() if args.dev else Config.for_production()
    loader = KnaDataLoader(config=config)
    
    logger.info(f"Loading data from: {args.file}")
    
    # Validate first if requested
    if not args.skip_validation:
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
    
    # Load data
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
    """Handle the validate command"""
    config = Config.for_development() if args.dev else Config.for_production()
    loader = KnaDataLoader(config=config)
    
    logger.info(f"Validating: {args.file}")
    validation = loader.validate_excel(args.file)
    
    if validation["valid"]:
        logger.info("✅ Validation PASSED")
        logger.info("Sheet information:")
        for sheet, count in validation["info"].items():
            logger.info(f"  {sheet:20s}: {count:>6} rows")
        
        if validation["warnings"]:
            logger.warning("Warnings:")
            for warning in validation["warnings"]:
                logger.warning(f"  - {warning}")
    else:
        logger.error("❌ Validation FAILED")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
        sys.exit(1)


def thumbnails_command(args):
    """Handle the thumbnails command"""
    config = Config.for_development() if args.dev else Config.for_production()
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
