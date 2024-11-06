# Network Scanner


[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/vortex4242/network-scanner/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)


## Author and Contacts

Kiril Ivanov

- Email: kirilivanov1312@protonmail.com
- Facebook: [Kiril Ivanov](https://www.facebook.com/kiril.ivanov.actual.profile)
- GitHub: [vortex4242](https://github.com/vortex4242)

For questions, suggestions, or issues, please contact me via email or open an issue in the [GitHub repository](https://github.com/vortex4242/network-scanner/issues).

## Overview

Network Scanner is a powerful Python-based network scanning tool. It provides detailed information about network topology, open ports, and operating systems of target hosts.

## Key Features

1. **Port Scanning**: The tool can scan a wide range of ports, allowing users to identify open, closed, and filtered ports on target hosts.

2. **OS Detection**: Using TCP/IP stack fingerprinting techniques, Network Scanner attempts to determine the operating system of the target host.

3. **Service Version Detection**: For open ports, the tool tries to identify the running service and its version.

4. **Asynchronous Scanning**: It uses asyncio for simultaneous scanning of multiple targets and ports, significantly improving performance.

5. **Customizable Port Ranges**: Users can specify specific port ranges to scan.

6. **Output Options**: Results can be displayed in the console or saved to a file for further analysis.

## How It Works

1. Network Scanner first sends TCP SYN packets to the specified ports on the target host.
2. Based on the response (or lack thereof), the tool determines the state of the port.
3. For open ports, the tool attempts to gather additional information about the running service.
4. Using characteristics such as TTL (Time To Live), window size, and TCP options, the tool makes an educated guess about the host's operating system.

## Applications

Network Scanner can be useful in various scenarios:

- **Network Inventory**: Quickly identify active hosts and services on the network.
- **Security Checks**: Detect unexpectedly open ports or services.
- **Network Troubleshooting**: Identify configuration issues or malfunctioning services.
- **Compliance Auditing**: Verify if network configuration meets organizational policies.

## Ethical Use

This tool is intended for ethical use on networks for which you have permission to test. Unauthorized network scanning may be illegal and unethical.

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

Copyright (c) 2024 Kiril Ivanov
