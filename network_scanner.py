import asyncio
import random
from models import ScanResult, db
from config import get_config
import logging

logger = logging.getLogger(__name__)

class Scanner:
    async def scan(self, targets, ports):
        results = []
        for target in targets:
            result = ScanResult(
                host=target,
                state='up',
                ports=[]
            )
            for port in range(int(ports.split('-')[0]), int(ports.split('-')[1])+1):
                if random.random() > 0.8:  # 20% chance the port is open
                    result.ports.append({
                        'port': port,
                        'state': 'open',
                        'service': f'service_{port}',
                        'product': f'product_{port}',
                        'version': f'1.0'
                    })
            results.append(result)
        return results

    async def get_service_info(self, host, port):
        return f"Simulated service info for {host}:{port}"

async def run_scan(scan_id):
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

if __name__ == '__main__':
    asyncio.run(run_scan(None))
