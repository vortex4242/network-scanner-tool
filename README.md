# Network Scanner Tool

A comprehensive network scanning tool with user authentication, advanced analysis features, visualization of scan results, real-time updates for ongoing scans, and support for scheduling regular scans.

## Features

- User authentication
- Advanced network scanning
- Result visualization
- Real-time scan updates
- Scheduled scans

## Requirements

- Python 3.7+
- Flask
- SQLAlchemy
- Other dependencies (see `requirements.txt`)

## Installation

1. Clone the repository:

git clone https://github.com/vortex4242/network-scanner-tool.git
cd network-scanner-tool


2. Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate


3. Install the required packages:

pip install -r requirements.txt


4. Initialize the database:

flask db init
flask db migrate
flask db upgrade


## Usage

1. Start the Flask development server:

flask run


2. Open a web browser and go to `http://localhost:5000`

3. Register a new user account and login

4. Use the web interface to:
- Perform network scans
- View scan and analysis results
- Schedule regular scans

## Running scans from the terminal

To run a network scan from the terminal:

python -c "from network_scanner import main; import asyncio; asyncio.run(main())"


This will run a scan using the default configuration. To customize the scan, you can modify the `config.json` file.

## Scheduling scans

Scans can be scheduled via the web interface. Go to your profile page and use the schedule form to set up recurring scans using cron statements.

## Contribution

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Testing

To run the tests:

```
python -m unittest discover tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Kiril Ivanov

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
