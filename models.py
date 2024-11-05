from setuptools import setup, find_packages

setup(
    name='network_scanner_tool',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-login',
        'flask-sqlalchemy',
        'flask-bcrypt',
        'matplotlib',
        'pandas',
        'apscheduler',
    ],
)

    config.json:

{
    "scanning": {
        "targets": ["localhost"],
        "ports": "1-1000",
        "max_threads": 10,
        "timeout": 60,
        "nmap_args": "-sV"
    },
    "database": {
        "uri": "sqlite:///network_scanner.db"
    },
    "logging": {
        "level": "INFO",
        "file": "network_scanner.log"
    }
}
