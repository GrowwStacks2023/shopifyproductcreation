import json
import logging

def read_config(config_path: str):
    logging.info(f"Attempting to read config file from: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            logging.info(f"Successfully loaded config with keys: {list(config_data.keys())}")
            return config_data
    except Exception as e:
        logging.error(f"Failed to read config file: {e}")
        raise
