# Network Scanner


[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/vortex4242/network-scanner/releases)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)


## Author and Contacts


**Kiril Ivanov**


- Email: [kirilivanov1312@protonmail.com](mailto:kirilivanov1312@protonmail.com)

- Facebook: [Kiril Ivanov](https://www.facebook.com/exploitdb1312420)

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

   ```bash

   git clone https://github.com/vortex4242/network-scanner.git

   cd network-scanner


# Advanced Usage and Contribution Guidelines

## Advanced Usage

### Custom Port Ranges

You can specify custom port ranges using the `-p` or `--ports` option. For example:

```
sudo python3 network_scanner.py -t 192.168.1.1 -p 1-1000,2000-3000
```

This will scan ports 1-1000 and 2000-3000.

### Output Formatting

By default, the scanner outputs results to the console. You can save results to a JSON file using the `-o` or `--output` option:

```
sudo python3 network_scanner.py -t 192.168.1.1 -o results.json
```

### Verbose Mode

Use the `-v` or `--verbose` flag for detailed output during scanning:

```
sudo python3 network_scanner.py -t 192.168.1.1 -v
```

### Scanning Multiple Targets

You can scan multiple targets by specifying them as a space-separated list:

```
sudo python3 network_scanner.py -t 192.168.1.1 192.168.1.2 10.0.0.1
```

## Contributing

### Setting Up Development Environment

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```
   git clone https://github.com/your-username/network-scanner.git
   cd network-scanner
   ```
3. Create a virtual environment and install dependencies:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Running Tests

Run the test suite using:

```
python -m unittest discover tests
```

### Adding New Features

1. Create a new branch for your feature:
   ```
   git checkout -b feature/your-feature-name
   ```
2. Implement your feature and add tests.
3. Run the test suite to ensure all tests pass.
4. Update the README.md and CHANGELOG.md files as necessary.
5. Commit your changes and push to your fork.
6. Open a pull request with a clear title and description.

### Coding Style

- Follow PEP 8 guidelines for Python code.
- Use meaningful variable and function names.
- Add docstrings to functions and classes.
- Comment your code where necessary.

### Reporting Issues

- Use the GitHub issue tracker to report bugs.
- Provide a clear and descriptive title.
- Include steps to reproduce the issue.
- Mention your operating system and Python version.

Thank you for contributing to the Network Scanner project!
