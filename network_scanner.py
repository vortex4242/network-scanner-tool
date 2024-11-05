import asyncio
import nmap
from .models import ScanResult
from . import db
from .config import get_config
import logging

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    async def scan(self, targets, ports):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._scan_sync, targets, ports)

    def _scan_sync(self, targets, ports):
        try:
            self.nm.scan(hosts=targets, ports=ports, arguments='-sV')
            results = []
            for host in self.nm.all_hosts():
                result = ScanResult(
                    host=host,
                    state=self.nm[host].state(),
                    ports=[]
                )
                for proto in self.nm[host].all_protocols():
                    lport = self.nm[host][proto].keys()
                    for port in lport:
                        result.ports.append({
                            'port': port,
                            'state': self.nm[host][proto][port]['state'],
                            'service': self.nm[host][proto][port]['name'],
                            'product': self.nm[host][proto][port]['product'],
                            'version': self.nm[host][proto][port]['version']
                        })
                results.append(result)
            return results
        except nmap.PortScannerError as e:
            logger.error(f"Nmap scan error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during scan: {str(e)}")
            raise

    async def get_service_info(self, host, port):
        # Implement service info retrieval logic here
        pass

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
