import asyncio
import logging
from flask import Flask
from network_scanner import run_scan
from config import init_config
from models import init_db, create_tables

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///network_scanner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_config(app)
init_db(app)
create_tables(app)

async def main():
    with app.app_context():
        await run_scan(None)

if __name__ == "__main__":
    asyncio.run(main())
