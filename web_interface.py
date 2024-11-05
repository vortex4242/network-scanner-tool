from flask import Flask, render_template, request, jsonify
from .database import ScanDatabase
from .network_scanner import Scanner
import asyncio

app = Flask(__name__)
db = ScanDatabase()
scanner = Scanner()

@app.route('/')
def index():
    scan_history = db.get_scan_history()
    return render_template('index.html', scan_history=scan_history)

@app.route('/scan_results/<int:scan_id>')
def scan_results(scan_id):
    results = db.get_scan_results(scan_id)
    return render_template('scan_results.html', results=results)

@app.route('/new_scan', methods=['GET', 'POST'])
def new_scan():
    if request.method == 'POST':
        targets = request.form.get('targets').split(',')
        ports = request.form.get('ports')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(scanner.scan(targets, ports))
        loop.close()
        
        db.save_scan_results(targets, ports, [r.to_dict() for r in results])
        return jsonify({"status": "success", "message": "Scan completed and results saved."})
    
    return render_template('new_scan.html')

@app.route('/analysis')
def analysis():
    scan_history = db.get_scan_history()
    total_scans = len(scan_history)
    total_hosts = sum(len(json.loads(scan['targets'])) for scan in scan_history)
    
    # Get the most recent scan results for analysis
    if scan_history:
        latest_scan = db.get_scan_results(scan_history[0]['id'])
        open_ports = sum(len([p for p in host['ports'] if p['state'] == 'open']) for host in latest_scan)
        most_common_ports = {}
        for host in latest_scan:
            for port in host['ports']:
                if port['state'] == 'open':
                    most_common_ports[port['port']] = most_common_ports.get(port['port'], 0) + 1
        most_common_ports = sorted(most_common_ports.items(), key=lambda x: x[1], reverse=True)[:5]
    else:
        open_ports = 0
        most_common_ports = []

    return render_template('analysis.html', total_scans=total_scans, total_hosts=total_hosts,
                           open_ports=open_ports, most_common_ports=most_common_ports)

if __name__ == '__main__':
    app.run(debug=True)
