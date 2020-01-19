import logging.config
import yaml

with open('logging.yml', 'r') as logging_yml:
    logging_config = yaml.safe_load(logging_yml.read())

logging.config.dictConfig(logging_config)
