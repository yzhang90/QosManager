"""
This is the configuration module.
"""

import logging
import sys
import os
import yaml
import re

LOG = logging.getLogger(__name__)

class QosConfig(object):
    
    def __init__(self):
        config_directory = os.path.join(os.path.dirname(__file__),
                                        "config")
        class_yaml = os.path.join(config_directory, "class.yaml")
        qos_yaml   = os.path.join(config_directory, "qos.yaml")
        queue_yaml = os.path.join(config_directory, "queue.yaml")

        try:
            with open(qos_yaml, 'r') as f:
                self.qos_config = yaml.load(f)
        except (IOError, OSError) :
            LOG.error("Failed to open qos.yaml")
            sys.exit("Exiting config module")
        
        try:
            with open(queue_yaml, 'r') as f:
                self.queue_config = yaml.load(f)
        except (IOError, OSError) :
            LOG.error("Failed to open queue.yaml")
            sys.exit("Exiting config module")
        
        #unit_parser = re.compile(r"(\d+\.?\d*)\s*(\w+)")
        #match = unit_parser.match(self.queue_config['queue'][9])
        #value = match.group(1)
        #unit = match.group(2)


if __name__ == "__main__":
    config = QosConfig()
