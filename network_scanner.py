
import asyncio
import socket
import struct
from typing import List, Dict, Any
from config import get_config
import logging
import time
import argparse
import json
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScanResult:
    def __init__(self, host: str, state: str, ports: List[Dict[str, Any]], scan_time: float, os_guess: str):
        self.host = host
        self.state = state
        self.ports = ports
        self.scan_time = scan_time
        self.os_guess = os_guess

    def to_dict(self) -> Dict[str, Any]:
        return {
            'host': self.host,
            'state': self.state,
            'ports': self.ports,
            'scan_time': self.scan_time,
            'os_guess': self.os_guess
        }

class Scanner:
    def _extract_tcp_options(self, options: bytes) -> Dict[str, Any]:
        i = 0
        extracted_options = {}
        while i < len(options) and i < 40:  # Limit to first 40 bytes to avoid application data
            if i + 1 >= len(options):
                break
            opt_type = options[i]
            opt_length = options[i+1] if opt_type != 1 else 1  # NOP has no length field

            if opt_type == 0:  # End of options
                break
            elif opt_type == 1:  # NOP
                i += 1
                continue
            elif opt_type == 2 and opt_length == 4:  # MSS
                extracted_options['MSS'] = struct.unpack('!H', options[i+2:i+4])[0]
            elif opt_type == 3 and opt_length == 3:  # Window Scale
                extracted_options['WScale'] = options[i+2]
            elif opt_type == 4 and opt_length == 2:  # SACK Permitted
                extracted_options['SACK'] = True
            elif opt_type == 8 and opt_length == 10:  # Timestamp
                extracted_options['Timestamp'] = struct.unpack('!II', options[i+2:i+10])

            i += opt_length

        return extracted_options

    def _guess_os(self, ttl: int, window_size: int, options: Dict[str, Any]) -> str:
        if ttl == 56:
            return f"Possible CDN or Load Balancer (Facebook/Google infrastructure) - Window Size: {window_size}"
        elif ttl == 64:
            if window_size == 65535:
                return "FreeBSD or OpenBSD"
            elif window_size in [5840, 14600, 29200]:
                return "Linux (kernel 2.4 and 2.6)"
            elif window_size == 16384:
                return "macOS (OS X)"
            elif window_size == 512:
                return "Linux (possibly virtualized)"
            elif window_size == 53270:
                return "Linux (possibly localhost)"
        elif ttl == 128:
            if window_size == 65535:
                return "Windows Server 2008, Vista, or 7"
            elif window_size == 8192:
                return "Windows 2000 or XP"
            elif window_size == 16384:
                return "Windows 2003 or 2008"
        elif ttl == 255:
            if window_size == 65535:
                return "Solaris or AIX"
            elif window_size == 4128:
                return "Cisco IOS"
            elif window_size == 53270:
                return "Linux (localhost)"
        
        if 'MSS' in options:
            mss = options['MSS']
            if mss == 1460:
                return f"Ethernet MTU (Windows or Linux) - TTL: {ttl}, Window Size: {window_size}"
            elif mss == 1380:
                return f"OpenBSD or NetBSD (Ethernet) - TTL: {ttl}, Window Size: {window_size}"
            elif mss == 1440:
                return f"Google server (GWS) - TTL: {ttl}, Window Size: {window_size}"
        
        return f"Unknown OS (TTL: {ttl}, Window Size: {window_size}, Options: {options})"

    async def _get_service_version(self, target: str, port: int) -> str:
        try:
            reader, writer = await asyncio.open_connection(target, port)
            writer.write(b"HEAD / HTTP/1.0\r\n\r\n")
            await writer.drain()
            response = await reader.read(1024)
            writer.close()
            await writer.wait_closed()
            
            response_str = response.decode('utf-8', errors='ignore')
            server_header = next((line for line in response_str.splitlines() if line.startswith("Server:")), None)
            if server_header:
                return server_header.split("Server:")[1].strip()
            return "Unknown"
        except Exception as e:
            logger.error(f"Error getting service version for {target}:{port}: {str(e)}")
            return "Unknown"

    async def scan_port(self, target: str, port: int) -> Dict[str, Any] | None:
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(1)
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: conn.connect_ex((target, port))
            )
            if result == 0:
                service = self._get_service_name(port)
                version = await self._get_service_version(target, port)
                return {
                    'port': port,
                    'state': 'open',
                    'service': service,
                    'version': version
                }
            conn.close()
        except Exception as e:
            logger.error(f"Error scanning port {target}:{port}: {str(e)}")
        return None

    @staticmethod
    def get_common_ports() -> List[int]:
        return [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]

    async def scan(self, targets: List[str], ports: str) -> List[ScanResult]:
        results = []
        start_port, end_port = map(int, ports.split('-'))
        common_ports = self.get_common_ports()
        for target in targets:
            logger.info(f"Scanning target: {target}")
            start_time = time.time()
            state = 'up'  # Assume the host is up if we can scan it
            open_ports = []
            
            # Scan common ports first
            common_port_tasks = [self.scan_port(target, port) for port in common_ports if start_port <= port <= end_port]
            common_port_results = await asyncio.gather(*common_port_tasks)
            open_ports.extend([result for result in common_port_results if result])
            
            # Scan remaining ports
            remaining_ports = [port for port in range(start_port, end_port + 1) if port not in common_ports]
            remaining_port_tasks = [self.scan_port(target, port) for port in remaining_ports]
            remaining_port_results = await asyncio.gather(*remaining_port_tasks)
            open_ports.extend([result for result in remaining_port_results if result])
            
            scan_time = time.time() - start_time
            os_guess = await self._get_os_guess(target)
            
            # Check if a large percentage of ports are reported as open
            total_ports = end_port - start_port + 1
            open_percentage = len(open_ports) / total_ports * 100
            logger.info(f"Open ports: {len(open_ports)}, Total ports: {total_ports}, Open percentage: {open_percentage:.2f}%")
            if open_percentage > 70:
                state = 'filtered'
                logger.warning(f"{open_percentage:.2f}% of ports reported as open for {target}. This may indicate a firewall or other protective measure.")
                open_ports = []  # Clear the list of open ports for filtered hosts
            
            result = ScanResult(host=target, state=state, ports=open_ports, scan_time=scan_time, os_guess=os_guess)
            logger.info(f"Scan completed for {target}. Time taken: {scan_time:.2f} seconds. State: {state}")
            results.append(result)
        
        return results

    def _get_service_name(self, port: int) -> str:
        common_ports = {
            80: 'http', 443: 'https', 22: 'ssh', 21: 'ftp',
            25: 'smtp', 110: 'pop3', 143: 'imap', 53: 'dns'
        }
        return common_ports.get(port, 'unknown')

    async def _get_os_guess(self, target: str) -> str:
        try:
            logger.info(f"Starting OS detection for {target}")
            target_ip = await asyncio.get_event_loop().run_in_executor(None, socket.gethostbyname, target)
            logger.info(f"Resolved {target} to IP: {target_ip}")
            
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            s.settimeout(2)
            logger.info("Socket created successfully")
            
            # Construct and send the packet
            packet = self._create_syn_packet(target_ip)
            await asyncio.get_event_loop().run_in_executor(None, s.sendto, packet, (target_ip, 0))
            logger.info("Packet sent successfully")
            
            # Receive the response
            data, addr = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, s.recvfrom, 1024),
                timeout=2
            )
            logger.info(f"Response received from {addr}")
            
            # Extract information from the response
            ip_header = data[:20]
            tcp_header = data[20:40]
            
            ttl = struct.unpack('!B', ip_header[8:9])[0]
            window_size = struct.unpack('!H', tcp_header[14:16])[0]
            options = data[40:]
            
            logger.info(f"Extracted TTL: {ttl}, Window Size: {window_size}")
            logger.info(f"TCP Options: {options.hex()}")
            
            os_guess = self._guess_os(ttl, window_size, options)
            logger.info(f"OS Guess for {target}: {os_guess}")
            return os_guess
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout during OS detection for {target}")
            return "Unknown (Timeout)"
        except Exception as e:
            logger.error(f"Error in OS detection for {target}: {str(e)}")
            return "Unknown (Error)"

    def _create_syn_packet(self, dest_ip: str) -> bytes:
        # IP header fields
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 20 + 20  # IP header + TCP header
        ip_id = 54321
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        ip_saddr = socket.inet_aton('0.0.0.0')
        ip_daddr = socket.inet_aton(dest_ip)
        
        ip_ihl_ver = (ip_ver << 4) + ip_ihl
        ip_header = struct.pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
        
        # TCP header fields
        tcp_source = 54321
        tcp_dest = 80
        tcp_seq = 0
        tcp_ack_seq = 0
        tcp_doff = 5
        tcp_fin = 0
        tcp_syn = 1
        tcp_rst = 0
        tcp_psh = 0
        tcp_ack = 0
        tcp_urg = 0
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0
        
        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
        
        tcp_header = struct.pack('!HHLLBBHHH', tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
        
        return ip_header + tcp_header

    def _guess_os(self, ttl: int, window_size: int, options: bytes) -> str:
        mss = self._extract_mss(options)
        
        if ttl == 56:
            return f"Possible CDN or Load Balancer (Facebook/Google infrastructure) - Window Size: {window_size}"
        elif ttl == 64:
            if window_size == 65535:
                return "FreeBSD or OpenBSD"
            elif window_size in [5840, 14600, 29200]:
                return "Linux (kernel 2.4 and 2.6)"
            elif window_size == 16384:
                return "macOS (OS X)"
            elif window_size == 512:
                return "Linux (possibly virtualized)"
            elif window_size == 53270:
                return "Linux (possibly localhost)"
        elif ttl == 128:
            if window_size == 65535:
                return "Windows Server 2008, Vista, or 7"
            elif window_size == 8192:
                return "Windows 2000 or XP"
            elif window_size == 16384:
                return "Windows 2003 or 2008"
        elif ttl == 255:
            if window_size == 65535:
                return "Solaris or AIX"
            elif window_size == 4128:
                return "Cisco IOS"
            elif window_size == 53270:
                return "Linux (localhost)"
        
        if mss:
            if mss == 1460:
                return f"Ethernet MTU (Windows or Linux) - TTL: {ttl}, Window Size: {window_size}"
            elif mss == 1380:
                return f"OpenBSD or NetBSD (Ethernet) - TTL: {ttl}, Window Size: {window_size}"
            elif mss == 1440:
                return f"Google server (GWS) - TTL: {ttl}, Window Size: {window_size}"
        
        return f"Unknown OS (TTL: {ttl}, Window Size: {window_size}, MSS: {mss if mss else 'N/A'})"

    def _extract_mss(self, options: bytes) -> int:
        i = 0
        while i < len(options) and i < 40:  # Limit to first 40 bytes to avoid application data
            opt_type = options[i]
            if opt_type == 0:  # End of options
                break
            if opt_type == 1:  # NOP
                i += 1
                continue
            if i + 1 >= len(options):
                break
            opt_length = options[i+1]
            if opt_type == 2 and opt_length == 4 and i + 3 < len(options):  # MSS option
                return struct.unpack('!H', options[i+2:i+4])[0]
            i += opt_length if opt_length > 1 else 1
        return 0

    async def _get_os_guess(self, target: str) -> str:
        try:
            logger.info(f"Starting OS detection for {target}")
            target_ip = await asyncio.get_event_loop().run_in_executor(None, socket.gethostbyname, target)
            logger.info(f"Resolved {target} to IP: {target_ip}")
            
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            s.settimeout(2)
            logger.info("Socket created successfully")
            
            # Construct and send the packet
            packet = self._create_syn_packet(target_ip)
            await asyncio.get_event_loop().run_in_executor(None, s.sendto, packet, (target_ip, 0))
            logger.info("Packet sent successfully")
            
            # Receive the response
            data, addr = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, s.recvfrom, 1024),
                timeout=2
            )
            logger.info(f"Response received from {addr}")
            
            # Extract information from the response
            ip_header = data[:20]
            tcp_header = data[20:40]
            
            ttl = struct.unpack('!B', ip_header[8:9])[0]
            window_size = struct.unpack('!H', tcp_header[14:16])[0]
            options = data[40:]
            
            logger.info(f"Extracted TTL: {ttl}, Window Size: {window_size}")
            logger.info(f"TCP Options: {options[:40].hex()}")  # Log only first 40 bytes of options
            
            os_guess = self._guess_os(ttl, window_size, options)
            logger.info(f"OS Guess for {target}: {os_guess}")
            return os_guess
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout during OS detection for {target}")
            return "Unknown (Timeout)"
        except Exception as e:
            logger.error(f"Error in OS detection for {target}: {str(e)}")
            return "Unknown (Error)"

async def run_scan(targets: List[str], ports: str) -> List[ScanResult]:
    scanner = Scanner()
    async def scan_target(target: str) -> ScanResult:
        logger.info(f"Scanning target: {target}")
        start_time = time.time()
        state = 'up'  # Assume the host is up if we can scan it
        start_port, end_port = map(int, ports.split('-'))
        
        port_tasks = [scanner.scan_port(target, port) for port in range(start_port, end_port + 1)]
        port_results = await asyncio.gather(*port_tasks)
        open_ports = [result for result in port_results if result and result['state'] == 'open']
        
        scan_time = time.time() - start_time
        os_guess = await scanner._get_os_guess(target)
        
        # Check if a large percentage of ports are reported as open
        total_ports = end_port - start_port + 1
        open_percentage = len(open_ports) / total_ports * 100
        logger.info(f"Open ports: {len(open_ports)}, Total ports: {total_ports}, Open percentage: {open_percentage:.2f}%")
        if open_percentage > 70:
            state = 'filtered'
            logger.warning(f"{open_percentage:.2f}% of ports reported as open for {target}. This may indicate a firewall or other protective measure.")
            open_ports = []  # Clear the list of open ports for filtered hosts
        
        result = ScanResult(host=target, state=state, ports=open_ports, scan_time=scan_time, os_guess=os_guess)
        logger.info(f"Scan completed for {target}. Time taken: {scan_time:.2f} seconds. State: {state}")
        return result

    return await asyncio.gather(*[scan_target(target) for target in targets])

def save_results_to_file(results: List[ScanResult], filename: str):
    with open(filename, 'w') as f:
        json.dump([result.to_dict() for result in results], f, indent=2)
    logger.info(f"Scan results saved to {filename}")

async def main():
    parser = argparse.ArgumentParser(description="Network Scanner")
    parser.add_argument("-t", "--targets", nargs="+", default=["localhost"], help="List of targets to scan")
    parser.add_argument("-p", "--ports", default="1-100", help="Port range to scan (e.g., '1-100' or '1-1000')")
    parser.add_argument("-o", "--output", help="Output file to save results")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    targets = args.targets
    ports = args.ports
    logger.info(f"Starting scan with targets: {targets} and ports: {ports}")
    
    try:
        results = await asyncio.wait_for(run_scan(targets, ports), timeout=300)  # 5 minutes timeout
        for result in results:
            print(f"Host: {result.host}")
            print(f"State: {result.state}")
            if result.state == 'filtered':
                print("  Host appears to be filtered (firewall or other protective measure)")
                print(f"Open ports: N/A (filtered)")
            else:
                print(f"Open ports: {len(result.ports)}")
                if result.ports:
                    for port in result.ports:
                        if 'service' in port:
                            print(f"  {port['port']}/tcp - {port['service']}")
                        else:
                            print(f"  {port['port']}/tcp - unknown")
                else:
                    print("  No open ports found")
            print(f"Total ports scanned: {int(ports.split('-')[1]) - int(ports.split('-')[0]) + 1}")
            if result.state != 'filtered':
                open_percentage = len(result.ports) / (int(ports.split('-')[1]) - int(ports.split('-')[0]) + 1) * 100
                print(f"Percentage of open ports: {open_percentage:.2f}%")
            print(f"Scan time: {result.scan_time:.2f} seconds")
            print(f"OS guess: {result.os_guess}")
            print("---")

        if args.output:
            save_results_to_file(results, args.output)

    except asyncio.TimeoutError:
        logger.error("Scan timed out after 5 minutes")

if __name__ == '__main__':
    asyncio.run(main())
