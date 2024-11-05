import aiosqlite
import json
from typing import List, Dict, Any
from datetime import datetime

class ScanDatabase:
    def __init__(self, db_file: str = 'scan_results.db'):
        """Initialize the ScanDatabase with the given database file."""
        self.db_file = db_file
        self.db = None

    async def connect(self):
        """Connect to the database and create tables if they don't exist."""
        self.db = await aiosqlite.connect(self.db_file)
        await self._create_tables()

    async def close(self):
        """Close the database connection."""
        if self.db:
            await self.db.close()

    async def _create_tables(self):
        """Create necessary tables if they don't exist."""
        async with self.db.cursor() as cursor:
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    targets TEXT NOT NULL,
                    ports TEXT NOT NULL
                )
            ''')
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    scan_id INTEGER,
                    host TEXT NOT NULL,
                    state TEXT NOT NULL,
                    ports TEXT NOT NULL,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                )
            ''')
            await self.db.commit()

    async def save_scan_results(self, user_id: int, targets: List[str], ports: str, results: List[Dict[str, Any]]):
        """Save scan results to the database."""
        timestamp = datetime.now().isoformat()
        async with self.db.cursor() as cursor:
            await cursor.execute('INSERT INTO scans (user_id, timestamp, targets, ports) VALUES (?, ?, ?, ?)',
                                 (user_id, timestamp, json.dumps(targets), ports))
            scan_id = cursor.lastrowid
            for result in results:
                await cursor.execute('INSERT INTO scan_results (scan_id, host, state, ports) VALUES (?, ?, ?, ?)',
                                     (scan_id, result['host'], result['state'], json.dumps(result['ports'])))
            await self.db.commit()

    async def get_scan_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get scan history for a specific user."""
        async with self.db.execute('SELECT id, timestamp, targets, ports FROM scans WHERE user_id = ? ORDER BY timestamp DESC', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(zip(['id', 'timestamp', 'targets', 'ports'], row)) for row in rows]

    async def get_scan_results(self, scan_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get scan results for a specific scan and user."""
        async with self.db.execute('SELECT s.id FROM scans s WHERE s.id = ? AND s.user_id = ?', (scan_id, user_id)) as cursor:
            if not await cursor.fetchone():
                return []  # User doesn't have permission to view this scan

        async with self.db.execute('SELECT host, state, ports FROM scan_results WHERE scan_id = ?', (scan_id,)) as cursor:
            rows = await cursor.fetchall()
            results = []
            for row in rows:
                result = dict(zip(['host', 'state', 'ports'], row))
                result['ports'] = json.loads(result['ports'])
                results.append(result)
            return results
