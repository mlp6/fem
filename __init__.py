import logging.config
import yaml
from pathlib import Path

package_path = Path(__file__).parent

with open(package_path / 'logging.yml', 'r') as logging_yml:
    logging_config = yaml.safe_load(logging_yml.read())

logging.config.dictConfig(logging_config)
