"""Main entry point for AquilaTrace platform."""

import argparse
import logging
from pathlib import Path
import sys

from src.core.config import Config
from src.core.logger import setup_logging
from src.api import create_app
import uvicorn


def setup_cli():
    """Setup command-line interface."""
    parser = argparse.ArgumentParser(
        description="AquilaTrace - Multi-layered Intelligence Platform for Financial Crime Detection"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Start API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="API host")
    api_parser.add_argument("--port", type=int, default=8000, help="API port")
    api_parser.add_argument("--workers", type=int, default=4, help="Number of workers")
    api_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    # Configuration command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.add_argument("--save", type=str, help="Save configuration to file")
    config_parser.add_argument("--load", type=str, help="Load configuration from file")
    
    # Analysis command
    analysis_parser = subparsers.add_parser("analyze", help="Run analysis")
    analysis_parser.add_argument("--input", type=str, required=True, help="Input data file")
    analysis_parser.add_argument("--output", type=str, help="Output results file")
    analysis_parser.add_argument("--type", type=str, default="transaction", 
                               choices=["transaction", "entity", "text", "blockchain"],
                               help="Analysis type")
    
    return parser


def start_api_server(args):
    """Start the API server."""
    config = Config.from_env()
    logger = setup_logging(__name__, level=config.log_level)
    
    logger.info(f"Starting AquilaTrace API server on {args.host}:{args.port}")
    
    app = create_app(config)
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        log_level=config.log_level.lower()
    )


def manage_config(args):
    """Manage configuration."""
    config = Config.from_env()
    
    if args.show:
        print("Current Configuration:")
        import json
        print(json.dumps(config.to_dict(), indent=2))
    
    if args.save:
        config.to_yaml(args.save)
        print(f"Configuration saved to {args.save}")
    
    if args.load:
        config = Config.from_yaml(args.load)
        print(f"Configuration loaded from {args.load}")


def run_analysis(args):
    """Run analysis on input data."""
    logger = setup_logging(__name__)
    
    from src.data import DataPipeline
    from src.ml import MLRegistry
    import pandas as pd
    
    logger.info(f"Running {args.type} analysis on {args.input}")
    
    # Load data
    if args.input.endswith('.csv'):
        df = pd.read_csv(args.input)
    elif args.input.endswith('.json'):
        df = pd.read_json(args.input)
    else:
        logger.error(f"Unsupported file format")
        return
    
    config = Config.from_env()
    
    if args.type == "transaction":
        pipeline = DataPipeline(config.ml_config.__dict__)
        results = pipeline.process_transactions(df)
        logger.info(f"Processed {len(results)} transactions")
    
    # Save results if specified
    if args.output:
        if args.output.endswith('.csv'):
            results.to_csv(args.output, index=False)
        elif args.output.endswith('.json'):
            results.to_json(args.output)
        logger.info(f"Results saved to {args.output}")


def main():
    """Main entry point."""
    parser = setup_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "api":
            start_api_server(args)
        elif args.command == "config":
            manage_config(args)
        elif args.command == "analyze":
            run_analysis(args)
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
