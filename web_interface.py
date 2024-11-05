from aioflask import Flask, render_template, request, jsonify
from flask_login import login_required, current_user
from .database import ScanDatabase
from .network_scanner import Scanner
import json
from typing import Dict, List, Any, Union, Tuple

app = Flask(__name__)
db = ScanDatabase()
scanner = Scanner()

# Configure app settings here
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a real secret key

@app.route('/')
@login_required
async def index() -> str:
    """Render the index page with scan history."""
    scan_history = await db.get_scan_history(current_user.id)
    return await render_template('index.html', scan_history=scan_history)

@app.route('/scan_results/<int:scan_id>')
@login_required
async def scan_results(scan_id: int) -> str:
    """Render the scan results page for a specific scan."""
    results = await db.get_scan_results(scan_id, current_user.id)
    if not results:
        return "Scan not found or you don't have permission to view it", 404
    return await render_template('scan_results.html', results=results)

@app.route('/new_scan', methods=['GET', 'POST'])
@login_required
async def new_scan() -> Union[str, Dict[str, str]]:
    """Handle new scan requests."""
    if request.method == 'POST':
        targets = request.form.get('targets', '').split(',')
        ports = request.form.get('ports', '')
        
        if not targets or not ports:
            return jsonify({"status": "error", "message": "Invalid input. Please provide targets and ports."}), 400
        
        try:
            results = await scanner.scan(targets, ports)
            await db.save_scan_results(current_user.id, targets, ports, [r.to_dict() for r in results])
            return jsonify({"status": "success", "message": "Scan completed and results saved."})
        except Exception as e:
            return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500
    
    return await render_template('new_scan.html')

@app.route('/analysis')
@login_required
async def analysis() -> str:
    """Render the analysis page with scan statistics."""
    scan_history = await db.get_scan_history(current_user.id)
    total_scans = len(scan_history)
    total_hosts = sum(len(json.loads(scan['targets'])) for scan in scan_history)
    
    open_ports = 0
    most_common_ports: List[Tuple[int, int]] = []
    
    if scan_history:
        try:
            latest_scan = await db.get_scan_results(scan_history[0]['id'], current_user.id)
            open_ports = sum(len([p for p in host['ports'] if p['state'] == 'open']) for host in latest_scan)
            port_count: Dict[int, int] = {}
            for host in latest_scan:
                for port in host['ports']:
                    if port['state'] == 'open':
                        port_count[port['port']] = port_count.get(port['port'], 0) + 1
            most_common_ports = sorted(port_count.items(), key=lambda x: x[1], reverse=True)[:5]
        except Exception as e:
            app.logger.error(f"Error processing scan results: {str(e)}")

    return await render_template('analysis.html', total_scans=total_scans, total_hosts=total_hosts,
                                 open_ports=open_ports, most_common_ports=most_common_ports)

if __name__ == '__main__':
    app.run(debug=True)
