"""
This module provides methods for Qos control.
"""

import logging

from ryu.lib.packet import ether_types
from ryu.lib.packet import in_proto as inet

import utils

class QosControl(object):
    
    def __init__(self, config):
        super(QosControl, self).__init__()
        queue_config = config.queue_config
        self.qos_config = config.qos_config
        self.bandwidth = utils.get_normalized_value(queue_config['bandwidth'])
        self.queues = {}
        for k, v in queue_config['queues'].iteritems():
            self.queues[k] = {'rate': utils.get_normalized_value(v),'used': 0}
        self.flows = {}
   
    # Add a classified flow into the flow dictionary.
    # Return the flowid of the classified flow, otherwise return None
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

    def remove_flow(self, flow_id):
        print self.flows
        self.flows.pop(flow_id, None)


    def get_Actions(self, datapath, flow_id, in_port, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Qos Actions
        if flow_id is not None:
            if datapath.id == 1 and out_port == 4 and in_port == 1:
                out_queue = 1
                actions = [parser.OFPActionSetQueue(out_queue),
                            parser.OFPActionOutput(out_port)]
            else:
                actions = [parser.OFPActionOutput(out_port)]
        # Normal Actions
        else:
            # Only do traffic shaping at switch 1
            if datapath.id == 1: 
                out_queue = 0
                actions = [parser.OFPActionSetQueue(out_queue),
                           parser.OFPActionOutput(out_port)]
            else:
                actions = [parser.OFPActionOutput(out_port)]

        return actions
