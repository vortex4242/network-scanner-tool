import os
import json
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator

class NetworkScannerConfig(BaseModel):
    """Configuration model for the Network Scanner."""
    API_RATE_LIMIT: int = Field(6, ge=1, le=60, description="Maximum API calls per minute")
    CACHE_EXPIRATION: int = Field(3600, ge=0, description="Cache expiration time in seconds")
    MAX_THREADS: int = Field(5, ge=1, le=100, description="Maximum number of concurrent scans")
    DEEP_SCAN: bool = Field(False, description="Whether to perform a deep scan by default")
    OUTPUT_FORMAT: str = Field("json", description="Default output format (json, csv, or both)")
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    @validator('OUTPUT_FORMAT')
    def validate_output_format(cls, v):
        if v not in ['json', 'csv', 'both']:
            raise ValueError("OUTPUT_FORMAT must be 'json', 'csv', or 'both'")
        return v

    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError("LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, or CRITICAL")
        return v

def load_config() -> NetworkScannerConfig:
    """Load configuration from environment variables or default values."""
    config_dict = {}
    for field in NetworkScannerConfig.__fields__:
        env_var = f'NETWORK_SCANNER_{field}'
        if env_var in os.environ:
            config_dict[field] = os.environ[env_var]
    
    return NetworkScannerConfig(**config_dict)

def load_config_from_file(file_path: str) -> NetworkScannerConfig:
    """Load configuration from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            config_dict = json.load(f)
        return NetworkScannerConfig(**config_dict)
    except Exception as e:
        logging.error(f"Error loading configuration from file: {str(e)}")
        return load_config()

CONFIG = load_config()

def get_config(key: str) -> Any:
    """Get a configuration value by key."""
    return getattr(CONFIG, key)

def validate_config() -> bool:
    """Validate the current configuration."""
    try:
        NetworkScannerConfig(**CONFIG.dict())
        return True
    except ValueError as e:
        logging.error(f"Configuration error: {str(e)}")
        return False
