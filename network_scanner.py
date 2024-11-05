import asyncio
import random
from typing import List, Dict, Any
from models import ScanResult, db
from config import get_config
import logging

logger = logging.getLogger(__name__)

class Scanner:
    async def scan(self, targets: List[str], ports: str) -> List[ScanResult]:
        """
        Simulate a network scan on the given targets and port range.
        
        :param targets: List of target hosts to scan
        :param ports: Port range to scan (e.g. '1-1000')
        :return: List of ScanResult objects
        """
        results = []
        start_port, end_port = map(int, ports.split('-'))
        for target in targets:
            result = ScanResult(
                host=target,
                state='up' if random.random() > 0.1 else 'down',  # 90% chance the host is up
                ports=[]
            )
            if result.state == 'up':
                for port in range(start_port, end_port + 1):
                    if random.random() > 0.95:  # 5% chance the port is open
                        result.ports.append({
                            'port': port,
                            'state': 'open',
                            'service': self._get_random_service(),
                            'product': self._get_random_product(),
                            'version': f'{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}'
                        })
            results.append(result)
        return results

    async def get_service_info(self, host: str, port: int) -> str:
        """Simulate getting detailed service information."""
        services = ['HTTP', 'HTTPS', 'FTP', 'SSH', 'SMTP', 'POP3', 'IMAP', 'DNS', 'TELNET']
        return f"Simulated {random.choice(services)} service info for {host}:{port}"

    def _get_random_service(self) -> str:
        services = ['http', 'https', 'ftp', 'ssh', 'smtp', 'pop3', 'imap', 'dns', 'telnet']
        return random.choice(services)

    def _get_random_product(self) -> str:
        products = ['Apache', 'Nginx', 'IIS', 'OpenSSH', 'Postfix', 'Dovecot', 'BIND', 'OpenTelnet']
        return random.choice(products)

async def run_scan(scan_id: int) -> None:
    """
    Run a network scan and save the results to the database.
    
    :param scan_id: ID of the scan to run
    """
    scanner = Scanner()
    targets = get_config('SCAN_TARGETS', ['localhost'])
    ports = get_config('SCAN_PORTS', '1-1000')
    
    try:
        results = await scanner.scan(targets, ports)
        for result in results:
            scan_result = ScanResult(
                scan_id=scan_id,
                host=result.host,
                state=result.state,
                ports=result.ports
            )
            db.session.add(scan_result)
        db.session.commit()
        logger.info(f"Scan {scan_id} results saved to database.")
        
        for result in results:
            logger.info(f"Host: {result.host} (State: {result.state})")
            for port in result.ports:
                logger.info(f"  Port {port['port']}: {port['state']} - {port['service']} {port['product']} {port['version']}")
                if port['state'] == 'open' and port['port'] in [80, 443, 8080]:
                    service_info = await scanner.get_service_info(result.host, port['port'])
                    logger.info(f"    Service Info: {service_info}")
    except ValueError as e:
        logger.error(f"Invalid input for scan {scan_id}: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during scan {scan_id}: {str(e)}")
        raise  # Re-raise the exception for higher-level error handling

if __name__ == '__main__':
    asyncio.run(run_scan(None))

