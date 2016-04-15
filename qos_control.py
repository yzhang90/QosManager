"""
This module provides methods for Qos control.
"""

import logging
import re

from ryu.lib.packet import ether_types
from ryu.lib.packet import in_proto as inet

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
        queue_config = config.queue_config
        self.qos_config = config.qos_config
        self.bandwidth = get_normalized_value(queue_config['bandwidth'])
        self.queues = {}
        for k, v in queue_config['queues'].iteritems():
            self.queues[k] = {'rate': get_normalized_value(v),'used': 0}
        self.flows = {}
    
    def add_flow(self, tc):
        if tc is not None:
            match = tc['match']
            traffic_type = tc['traffic_type']
            flow_id = tc['flow_id']
            if flow_id is None:
                return None
            if traffic_type is not None:
                if flow_id not in self.flows:
                    self.flows[flow_id] = {'traffic_type': traffic_type}
                return flow_id

        return None


    def get_Actions(self, datapath, flowid, in_port, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #Qos Actions
        if flowid is not None:
            if datapath.id == 1 and out_port == 4 and in_port == 1:
                out_queue = 1
                actions = [parser.OFPActionSetQueue(out_queue),
                            parser.OFPActionOutput(out_port)]
            else:
                actions = [parser.OFPActionOutput(out_port)]
        #Normal Actions
        else:
            out_queue = 0
            actions = [parser.OFPActionSetQueue(out_queue),
                       parser.OFPActionOutput(out_port)]

        return actions
