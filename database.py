import sqlite3
import json
from typing import List, Dict, Any
from datetime import datetime

class ScanDatabase:
    def __init__(self, db_file: str = 'scan_results.db'):
        self.db_file = db_file
        self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    targets TEXT NOT NULL,
                    ports TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    scan_id INTEGER,
                    host TEXT NOT NULL,
                    state TEXT NOT NULL,
                    ports TEXT NOT NULL,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                )
            ''')
            conn.commit()

    def save_scan_results(self, targets: List[str], ports: str, results: List[Dict[str, Any]]):
        timestamp = datetime.now().isoformat()
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO scans (timestamp, targets, ports) VALUES (?, ?, ?)',
                           (timestamp, json.dumps(targets), ports))
            scan_id = cursor.lastrowid
            for result in results:
                cursor.execute('INSERT INTO scan_results (scan_id, host, state, ports) VALUES (?, ?, ?, ?)',
                               (scan_id, result['host'], result['state'], json.dumps(result['ports'])))
            conn.commit()

    def get_scan_history(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, timestamp, targets, ports FROM scans ORDER BY timestamp DESC')
            return [dict(row) for row in cursor.fetchall()]

    def get_scan_results(self, scan_id: int) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT host, state, ports FROM scan_results WHERE scan_id = ?', (scan_id,))
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['ports'] = json.loads(result['ports'])
                results.append(result)
            return results
