import argparse
import asyncio
from typing import List

from .config import Config, get_config, validate_config
from .network_scanner import Scanner
from .scan_comparison import compare_scans
from .logging_config import setup_logging

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Network Scanner CLI")
    parser.add_argument('--targets', nargs='+', help='IP addresses or ranges to scan')
    parser.add_argument('--ports', help='Ports to scan (e.g., "80,443,8080" or "1-1000")')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--compare', help='Path to previous scan results for comparison')
    parser.add_argument('--output', help='Output file for scan results')
    return parser.parse_args()

async def run_scan(targets: List[str], ports: str) -> dict:
    scanner = Scanner()
    return await scanner.scan(targets, ports)

def save_results(results: dict, filename: str):
    # Implementation for saving results to a file

def load_previous_results(filename: str) -> dict:
    # Implementation for loading previous scan results from a file

async def main():
    setup_logging()
    args = parse_arguments()

    if args.config:
        Config(args.config)  # Load specified config file

    if not validate_config():
        print("Invalid configuration. Please check your config file.")
        return

    targets = args.targets or get_config('scanning', 'targets')
    ports = args.ports or get_config('scanning', 'ports')

    if not targets:
        print("No targets specified. Please provide targets via CLI or config file.")
        return

    results = await run_scan(targets, ports)

    if args.output:
        save_results(results, args.output)

    if args.compare:
        previous_results = load_previous_results(args.compare)
        changes = compare_scans(results, previous_results)
        for change in changes:
            print(change)

if __name__ == '__main__':
    asyncio.run(main())
