import os
import logging

# Default configuration
DEFAULT_CONFIG = {
    'API_RATE_LIMIT': 6,  # Maximum calls per minute
    'CACHE_EXPIRATION': 3600,  # Cache results for 1 hour
    'MAX_THREADS': 5,  # Maximum number of concurrent scans
    'DEEP_SCAN': False,  # Whether to perform a deep scan by default
    'OUTPUT_FORMAT': 'json',  # Default output format (json or csv)
    'LOG_LEVEL': 'INFO',  # Logging level
}

# Try to load configuration from environment variables
CONFIG = {
    key: os.environ.get(f'NETWORK_SCANNER_{key}', DEFAULT_CONFIG[key])
    for key in DEFAULT_CONFIG
}

# Convert types
CONFIG['API_RATE_LIMIT'] = int(CONFIG['API_RATE_LIMIT'])
CONFIG['CACHE_EXPIRATION'] = int(CONFIG['CACHE_EXPIRATION'])
CONFIG['MAX_THREADS'] = int(CONFIG['MAX_THREADS'])
CONFIG['DEEP_SCAN'] = CONFIG['DEEP_SCAN'].lower() == 'true'

# Function to get configuration value
def get_config(key):
    return CONFIG.get(key, DEFAULT_CONFIG.get(key))

def validate_config():
    errors = []
    
    if CONFIG['API_RATE_LIMIT'] < 1 or CONFIG['API_RATE_LIMIT'] > 60:
        errors.append("API_RATE_LIMIT must be between 1 and 60")
    
    if CONFIG['CACHE_EXPIRATION'] < 0:
        errors.append("CACHE_EXPIRATION must be non-negative")
    
    if CONFIG['MAX_THREADS'] < 1 or CONFIG['MAX_THREADS'] > 100:
        errors.append("MAX_THREADS must be between 1 and 100")
    
    if CONFIG['OUTPUT_FORMAT'] not in ['json', 'csv', 'both']:
        errors.append("OUTPUT_FORMAT must be 'json', 'csv', or 'both'")
    
    if CONFIG['LOG_LEVEL'] not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        errors.append("LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, or CRITICAL")
    
    if errors:
        for error in errors:
            logging.error(f"Configuration error: {error}")
        return False
    
    return True
