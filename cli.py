import argparse
import asyncio
import json
from typing import List, Any

from .config import NetworkScannerConfig, get_config, validate_config
from .network_scanner import Scanner, ScanResult
from .scan_comparison import compare_scan_results
from .logging_config import setup_logging, get_logger

logger = get_logger(__name__)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Network Scanner CLI")
    parser.add_argument('--targets', nargs='+', help='IP addresses or ranges to scan')
    parser.add_argument('--ports', help='Ports to scan (e.g., "80,443,8080" or "1-1000")')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--compare', help='Path to previous scan results for comparison')
    parser.add_argument('--output', help='Output file for scan results')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Increase output verbosity')
    return parser.parse_args()

async def run_scan(targets: List[str], ports: str) -> List[ScanResult]:
    scanner = Scanner()
    return await scanner.scan(targets, ports)

def save_results(results: List[ScanResult], filename: str) -> None:
    try:
        with open(filename, 'w') as f:
            json.dump([result.to_dict() for result in results], f, indent=2)
        logger.info(f"Scan results saved to {filename}")
    except IOError as e:
        logger.error(f"Error saving results to {filename}: {str(e)}")

def load_previous_results(filename: str) -> List[ScanResult]:
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return [ScanResult.from_dict(item) for item in data]
    except IOError as e:
        logger.error(f"Error loading previous results from {filename}: {str(e)}")
        return []

def print_scan_results(results: List[ScanResult], verbosity: int) -> None:
    logger.info("Scan Results:")
    for result in results:
        logger.info(f"Host: {result.host}")
        logger.info(f"  State: {result.state}")
        if verbosity > 0:
            logger.info("  All Ports:")
            for port in result.ports:
                logger.info(f"    {port['port']}/tcp - {port['state']} - {port.get('service', 'unknown')}")
        else:
            logger.info("  Open Ports:")
            for port in result.ports:
                if port['state'] == 'open':
                    logger.info(f"    {port['port']}/tcp - {port.get('service', 'unknown')}")
        logger.info("---")

import time

async def main() -> None:
    setup_logging()
    args = parse_arguments()

    try:
        if args.config:
            config = NetworkScannerConfig.parse_file(args.config)
        else:
            config = NetworkScannerConfig()

        if not validate_config():
            logger.error("Invalid configuration. Please check your config file.")
            return

        targets = args.targets or config.SCAN_TARGETS
        ports = args.ports or config.SCAN_PORTS

        if not targets:
            logger.error("No targets specified. Please provide targets via CLI or config file.")
            return

        logger.info(f"Starting scan on targets: {targets}, ports: {ports}")
        start_time = time.time()
        results = await run_scan(targets, ports)
        end_time = time.time()
        scan_duration = end_time - start_time
        logger.info(f"Scan completed successfully in {scan_duration:.2f} seconds")

        print_scan_results(results, args.verbose)

        if args.output:
            save_results(results, args.output)
            logger.info(f"Results saved to {args.output}")

        if args.compare:
            previous_results = load_previous_results(args.compare)
            changes = compare_scan_results(results, previous_results)
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
