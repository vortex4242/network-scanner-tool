
import os
import pickle
import logging
from typing import Dict, List, Optional
import json
import datetime
from jinja2 import Template
import csv
import subprocess
import argparse
import xml.etree.ElementTree as ET
from collections import Counter

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file: str = 'config.json') -> Dict:
    """Load configuration from a JSON file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_file}")
        return config
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading configuration: {e}")
        return {}

def save_scan_results(report: Dict, filename: str = 'previous_scan.pkl') -> None:
    """Save the scan results to a file using pickle."""
    try:
        with open(filename, 'wb') as f:
            pickle.dump(report, f)
        logger.info(f"Scan results saved to {filename}")
    except IOError as e:
        logger.error(f"Error saving scan results: {e}")
        raise

def load_previous_scan_results(filename: str = 'previous_scan.pkl') -> Optional[Dict]:
    """Load the previous scan results from a file."""
    if os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                report = pickle.load(f)
            logger.info(f"Previous scan results loaded from {filename}")
            return report
        except (IOError, pickle.UnpicklingError) as e:
            logger.error(f"Error loading previous scan results: {e}")
            return None
    logger.info("No previous scan results found")
    return None

def compare_scan_results(current_report: Dict, previous_report: Optional[Dict]) -> List[str]:
    """Compare the current scan results with the previous scan results."""
    if not previous_report:
        return ["No previous scan results available for comparison."]

    changes = []
    try:
        current_hosts = {host['host']: host for host in current_report['hosts']}
        previous_hosts = {host['host']: host for host in previous_report['hosts']}

        # Check for new or removed hosts
        new_hosts = set(current_hosts.keys()) - set(previous_hosts.keys())
        removed_hosts = set(previous_hosts.keys()) - set(current_hosts.keys())

        for host in new_hosts:
            changes.append(f"New host detected: {host}")
        for host in removed_hosts:
            changes.append(f"Host no longer detected: {host}")

        # Check for changes in existing hosts
        for host, current_info in current_hosts.items():
            if host in previous_hosts:
                previous_info = previous_hosts[host]
                
                # Check for state changes
                if current_info['state'] != previous_info['state']:
                    changes.append(f"Host {host} state changed from {previous_info['state']} to {current_info['state']}")
                
                # Check for port changes
                current_ports = {port['port']: port for port in current_info['ports']}
                previous_ports = {port['port']: port for port in previous_info['ports']}
                
                for port, current_port_info in current_ports.items():
                    if port not in previous_ports:
                        changes.append(f"New open port on {host}: {port} ({current_port_info['service']})")
                    elif current_port_info != previous_ports[port]:
                        changes.append(f"Port {port} on {host} changed: {previous_ports[port]} -> {current_port_info}")
                
                for port in previous_ports:
                    if port not in current_ports:
                        changes.append(f"Port {port} on {host} is no longer open")

        logger.info("Scan comparison completed successfully")
        return changes if changes else ["No changes detected since the last scan."]
    except KeyError as e:
        logger.error(f"Error comparing scan results: Invalid report structure - {e}")
        return [f"Error comparing scan results: Invalid report structure - {e}"]
    except Exception as e:
        logger.error(f"Unexpected error during scan comparison: {e}")
        return [f"Unexpected error during scan comparison: {e}"]


def run_nmap_scan(target: str, timeout: int = 120, nmap_args: str = "-p- -T4", scan_type: str = "normal") -> Dict:
    """Run an nmap scan on the specified target."""
    try:
        logger.info(f"Starting {scan_type} nmap scan on target: {target}")
        logger.info(f"Using nmap arguments: {nmap_args}")
        command = ['nmap', '-sV', '-oX', '-']
        if scan_type == "detailed":
            command.extend(['--script=default,vuln'])
        # Remove duplicate -p- if it's already in nmap_args
        if '-p-' not in nmap_args:
            command.append('-p-')
        command.extend(nmap_args.split())
        command.append(target)
        logger.debug(f"Full nmap command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=timeout)
        logger.debug(f"nmap scan completed. Parsing results...")
        root = ET.fromstring(result.stdout)
        hosts = []
        for host in root.findall('.//host'):
            ip = host.find('.//address[@addrtype="ipv4"]').get('addr')
            state = host.find('.//status').get('state')
            ports = []
            for port in host.findall('.//port'):
                port_id = port.get('portid')
                service = port.find('.//service')
                service_name = service.get('name', 'unknown') if service is not None else 'unknown'
                service_product = service.get('product', '') if service is not None else ''
                service_version = service.get('version', '') if service is not None else ''
                script_output = []
                for script in port.findall('.//script'):
                    script_output.append({
                        'name': script.get('id'),
                        'output': script.get('output')
                    })
                ports.append({
                    'port': int(port_id),
                    'service': service_name,
                    'product': service_product,
                    'version': service_version,
                    'scripts': script_output
                })
            hosts.append({'host': ip, 'state': state, 'ports': ports})
        logger.info(f"Scan completed. Found {len(hosts)} hosts.")
        return {'hosts': hosts}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running nmap scan: {e}")
        logger.error(f"nmap stderr: {e.stderr}")
        return {'hosts': []}
    except subprocess.TimeoutExpired:
        logger.error(f"nmap scan timed out after {timeout} seconds")
        return {'hosts': []}
    except Exception as e:
        logger.error(f"Unexpected error during nmap scan: {e}")
        return {'hosts': []}


def generate_html_report(current_report: Dict, changes: List[str]) -> str:
    """Generate an HTML report of the scan results and changes."""
    template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Network Scan Report</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1, h2, h3 { color: #2c3e50; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .changes { background-color: #e6f3ff; padding: 10px; border-radius: 5px; }
            .chart { width: 100%; height: 300px; }
            .vulnerability { color: #d9534f; }
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>Network Scan Report</h1>
        <p>Generated on: {{ timestamp }}</p>
        
        <h2>Scan Results</h2>
        {% for host in hosts %}
        <h3>Host: {{ host.host }} ({{ host.state }})</h3>
        <table>
            <tr>
                <th>Port</th>
                <th>Service</th>
                <th>Product</th>
                <th>Version</th>
                <th>Vulnerabilities</th>
            </tr>
            {% for port in host.ports %}
            <tr>
                <td>{{ port.port }}</td>
                <td>{{ port.service }}</td>
                <td>{{ port.product }}</td>
                <td>{{ port.version }}</td>
                <td>
                    {% for script in port.scripts %}
                    {% if 'vuln' in script.name %}
                    <p class="vulnerability">{{ script.name }}: {{ script.output }}</p>
                    {% endif %}
                    {% endfor %}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% endfor %}
        
        <h2>Changes Since Last Scan</h2>
        <div class="changes">
            {% for change in changes %}
            <p>{{ change }}</p>
            {% endfor %}
        </div>

        <h2>Port Distribution</h2>
        <div id="portChart" class="chart"></div>

        <h2>Service Version Distribution</h2>
        <div id="versionChart" class="chart"></div>

        <script>
            var portData = {{ port_data | tojson }};
            var data = [{
                x: Object.keys(portData),
                y: Object.values(portData),
                type: 'bar'
            }];
            var layout = {
                title: 'Open Ports Distribution',
                xaxis: { title: 'Port' },
                yaxis: { title: 'Number of Hosts' }
            };
            Plotly.newPlot('portChart', data, layout);

            var versionData = {{ version_data | tojson }};
            var versionChartData = [{
                labels: Object.keys(versionData),
                values: Object.values(versionData),
                type: 'pie'
            }];
            var versionLayout = {
                title: 'Service Version Distribution'
            };
            Plotly.newPlot('versionChart', versionChartData, versionLayout);
        </script>
    </body>
    </html>
    """)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate port and version distribution
    port_data = Counter()
    version_data = Counter()
    for host in current_report['hosts']:
        for port in host['ports']:
            port_data[port['port']] += 1
            version_key = f"{port['product']} {port['version']}"
            version_data[version_key] += 1
    
    html_content = template.render(
        hosts=current_report['hosts'],
        changes=changes,
        timestamp=timestamp,
        port_data=dict(port_data),
        version_data=dict(version_data)
    )
    
    return html_content

def main():
    parser = argparse.ArgumentParser(description="Network Scanner and Comparison Tool")
    parser.add_argument("--config", help="Path to configuration file", default="config.json")
    parser.add_argument("--target", help="Target to scan (overrides config file)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    config = load_config(args.config)
    target = args.target or config.get('target', 'localhost')
    nmap_timeout = config.get('nmap_timeout', 120)
    nmap_args = config.get('nmap_args', '-p- -T4')
    scan_type = config.get('scan_type', 'normal')

    logger.info(f"Starting {scan_type} scan with target: {target}")
    logger.info(f"Scan timeout: {nmap_timeout} seconds")
    logger.info(f"nmap arguments: {nmap_args}")

    current_report = run_nmap_scan(target, nmap_timeout, nmap_args, scan_type)
    save_scan_results(current_report)
    previous_report = load_previous_scan_results()
    changes = compare_scan_results(current_report, previous_report)
    html_report = generate_html_report(current_report, changes)
    save_html_report(html_report)
    export_to_csv(current_report)
    
    logger.info("Scan comparison and report generation completed. Check scan_report.html and scan_results.csv for details.")


def save_html_report(html_content: str, filename: str = 'scan_report.html') -> None:
    """Save the HTML report to a file."""
    try:
        with open(filename, 'w') as f:
            f.write(html_content)
        logger.info(f"HTML report saved to {filename}")
    except IOError as e:
        logger.error(f"Error saving HTML report: {e}")
        raise

def export_to_csv(report: Dict, filename: str = 'scan_results.csv') -> None:
    """Export scan results to a CSV file."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['host', 'state', 'port', 'service', 'product', 'version']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for host in report['hosts']:
                for port in host['ports']:
                    writer.writerow({
                        'host': host['host'],
                        'state': host['state'],
                        'port': port['port'],
                        'service': port['service'],
                        'product': port['product'],
                        'version': port['version']
                    })
        logger.info(f"Scan results exported to CSV: {filename}")
    except IOError as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise


if __name__ == "__main__":
    main()
