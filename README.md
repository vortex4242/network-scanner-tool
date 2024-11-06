
# Network Scanner

A Python-based network scanner with OS detection capabilities.

## Features

- Port scanning with customizable port ranges
- OS detection based on TCP/IP stack fingerprinting
- Service version detection for open ports
- Asynchronous scanning for improved performance
- Output results to console or JSON file

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/network-scanner.git
   cd network-scanner
   ```

2. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the scanner with sudo privileges:

```
sudo python3 network_scanner.py -t [TARGET_IPS] -p [PORT_RANGE] -o [OUTPUT_FILE] -v
```

Arguments:
- `-t, --targets`: List of target IP addresses to scan (default: localhost)
- `-p, --ports`: Port range to scan (e.g., '1-100' or '1-1000', default: 1-100)
- `-o, --output`: Output file to save results in JSON format
- `-v, --verbose`: Enable verbose output

Example:
```
sudo python3 network_scanner.py -t 192.168.1.1 8.8.8.8 -p 1-1000 -o results.json -v
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
