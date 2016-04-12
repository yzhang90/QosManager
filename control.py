"""
This module provides methods for Qos control.
"""

import logging
import yaml
import re

import config

def main_unit(v)  : return int(v)
def kbps2bps(kbps): return int(float(kbps)*1000)
def mbps2bps(mbps): return int(float(mbps)*1000000)

normalize_unit = {
    'bps' : main_unit,
    'Kbps': kbps2bps,
    'Mbps': mbps2bps
    }

def get_normalized_value(str):
    unit_parser = re.compile(r"(\d+\.?\d*)\s*(\w+)")
    match = unit_parser.match(str)
    unit = match.group(2)
    return normalize_unit[unit](match.group(1))

class QosControl(object):
    
    def __init__(self, config):
        super(QosControl, self).__init__()
        qc = config.queue_config
        self.bandwidth = get_normalized_value(qc['bandwidth'])
        self.queues = {}
        
        

    def compute_normalActions(self, datapath, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        actions = [parser.OFPActionOutput(out_port)]

        return actions

    def compute_QosActions(self, datapath, in_port, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if datapath.id == 1 and out_port == 4 and in_port == 1:
            out_queue = 1
            actions = [parser.OFPActionSetQueue(out_queue),
                        parser.OFPActionOutput(out_port)]
        else:
            actions = [parser.OFPActionOutput(out_port)]

        return actions


if __name__ == '__main__':
    config = config.QosConfig() 
    control = QosControl(config)
