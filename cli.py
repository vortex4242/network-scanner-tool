import argparse
import asyncio
import json
from typing import List, Dict, Any

from .config import Config, get_config, validate_config
from .network_scanner import Scanner
from .scan_comparison import compare_scans
from .logging_config import setup_logging, get_logger

logger = get_logger(__name__)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Network Scanner CLI")
    parser.add_argument('--targets', nargs='+', help='IP addresses or ranges to scan')
    parser.add_argument('--ports', help='Ports to scan (e.g., "80,443,8080" or "1-1000")')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--compare', help='Path to previous scan results for comparison')
    parser.add_argument('--output', help='Output file for scan results')
    return parser.parse_args()

async def run_scan(targets: List[str], ports: str) -> Dict[str, Any]:
    scanner = Scanner()
    return await scanner.scan(targets, ports)

def save_results(results: Dict[str, Any], filename: str) -> None:
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Scan results saved to {filename}")
    except IOError as e:
        logger.error(f"Error saving results to {filename}: {str(e)}")

def load_previous_results(filename: str) -> Dict[str, Any]:
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except IOError as e:
        logger.error(f"Error loading previous results from {filename}: {str(e)}")
        return {}

async def main() -> None:
    setup_logging()
    args = parse_arguments()

    try:
        if args.config:
            Config(args.config)  # Load specified config file

        if not validate_config():
            logger.error("Invalid configuration. Please check your config file.")
            return

        targets = args.targets or get_config('scanning', 'targets')
        ports = args.ports or get_config('scanning', 'ports')

        if not targets:
            logger.error("No targets specified. Please provide targets via CLI or config file.")
            return

        logger.info(f"Starting scan on targets: {targets}, ports: {ports}")
        results = await run_scan(targets, ports)
        logger.info("Scan completed successfully")

        if args.output:
            save_results(results, args.output)

        if args.compare:
            previous_results = load_previous_results(args.compare)
            changes = compare_scans(results, previous_results)
            if changes:
                logger.info("Changes detected since last scan:")
                for change in changes:
                    logger.info(change)
            else:
                logger.info("No changes detected since last scan")

    except Exception as e:
        logger.exception(f"An error occurred during execution: {str(e)}")

if __name__ == '__main__':
    asyncio.run(main())
