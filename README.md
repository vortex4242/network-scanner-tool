
# Network Scanner


A comprehensive Python-based network scanner with advanced OS detection capabilities.


## Overview


This Network Scanner is a powerful tool designed for network administrators, security professionals, and enthusiasts. It provides detailed insights into network topology, open ports, and operating systems of target hosts.


## Features


- **Port Scanning**: Customizable port ranges for thorough network analysis.

- **OS Detection**: Advanced TCP/IP stack fingerprinting for accurate OS identification.

- **Service Version Detection**: Identifies services running on open ports.

- **Asynchronous Scanning**: Utilizes asyncio for high-performance, concurrent scanning.

- **Flexible Output**: Console display and JSON file export options.

- **Custom TCP Packet Crafting**: Uses raw sockets for precise control over TCP packets.

- **Intelligent Port Selection**: Prioritizes scanning of common ports for efficiency.


## Requirements


- Python 3.7+

- Root/Administrator privileges (for raw socket operations)


## Installation


1. Clone the repository:

   ```

   git clone https://github.com/vortex4242/network-scanner.git

   cd network-scanner

   ```


2. (Optional) Create and activate a virtual environment:

   ```

   python3 -m venv venv

   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

   ```


3. Install the required packages:

   ```

   pip install -r requirements.txt

   ```


## Usage


Run the scanner with sudo/administrator privileges:


```

sudo python3 network_scanner.py -t [TARGET_IPS] -p [PORT_RANGE] -o [OUTPUT_FILE] -v

```


### Arguments


- `-t, --targets`: List of target IP addresses to scan (default: localhost)

- `-p, --ports`: Port range to scan (e.g., '1-100' or '1-1000', default: 1-100)

- `-o, --output`: Output file to save results in JSON format

- `-v, --verbose`: Enable verbose output for detailed scanning information


### Examples


1. Scan a single target for common ports:

   ```

   sudo python3 network_scanner.py -t 192.168.1.1 -p 1-1000

   ```


2. Scan multiple targets with verbose output:

   ```

   sudo python3 network_scanner.py -t 192.168.1.1 8.8.8.8 -p 1-100 -v

   ```


3. Scan and save results to a file:

   ```

   sudo python3 network_scanner.py -t 192.168.1.0/24 -p 1-1000 -o network_scan_results.json

   ```


## How It Works


1. **Port Scanning**: The scanner attempts to establish TCP connections to specified ports on target hosts.

2. **OS Detection**: Analyzes TCP/IP characteristics like TTL, Window Size, and TCP Options to guess the OS.

3. **Service Detection**: For open ports, attempts to identify the service and its version.

4. **Asynchronous Operations**: Utilizes Python's asyncio to perform concurrent scans for improved speed.


## Output Interpretation


- **Open Ports**: Ports that accept TCP connections.

- **Filtered Ports**: Ports that don't respond or are blocked by a firewall.

- **OS Guess**: Best estimate of the target's operating system based on network fingerprints.

- **Service Versions**: Identified services running on open ports.


## Limitations


- Requires root/administrator privileges for raw socket operations.

- OS detection accuracy may vary depending on network conditions and target configurations.

- Some firewalls or intrusion detection systems may detect and block the scan attempts.


## Contributing


Contributions to improve the Network Scanner are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.


## License


This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Disclaimer


This tool is for educational and ethical testing purposes only. Ensure you have permission before scanning any networks or systems you do not own or have explicit permission to test.


## Contact


For questions, suggestions, or issues, please open an issue on the [GitHub repository](https://github.com/vortex4242/network-scanner/issues).
