"""
This module provides methods for Qos control.
"""

import logging
import heapq

from ryu.lib.packet import ether_types
from ryu.lib.packet import in_proto as inet

import utils

class QosControl(object):
    
    def __init__(self, config):
        super(QosControl, self).__init__()
        self.qos_config = config.qos_config
        for k in self.qos_config:
            rec_rate = self.qos_config[k]['recommended']
            min_rate = self.qos_config[k]['minimum']
            self.qos_config[k]['recommended'] = utils.get_normalized_value(rec_rate)
            self.qos_config[k]['minimum']     = utils.get_normalized_value(min_rate)
        queue_config = config.queue_config
        self.bandwidth = utils.get_normalized_value(queue_config['bandwidth'])
        self.queues = {}
        for k, v in queue_config['queues'].iteritems():
            self.queues[k] = {'rate': utils.get_normalized_value(v),'used': 0}
        self.flows = {}


    # Based on bandwith, queues and flows, compute the optimal assignment of 
    # classified flows to queues.
    def compute_optimal_assignment(self):
        total_rate = 0
        # First clear queue usage table and flow assignment table
        for k in self.queues:
            self.queues[k]['used'] = 0
        for k in self.flows:
            self.flows[k]['queue'] = 0
        # Second construct sorted list from the flows dictionary
        tmp = []
        flows_assigned = []
        for k, v in self.flows.iteritems():
            score = self.qos_config[v['traffic_type']]['priority']
            rate = self.qos_config[v['traffic_type']]['recommended']
            criteria = {'score': score, 'rate': rate}
            tmp.append((k, criteria))

            score = self.qos_config[v['traffic_type']]['priority'] * 0.5
            rate = self.qos_config[v['traffic_type']]['minimum']
            criteria = {'score': score, 'rate': rate}
            tmp.append((k, criteria))

        sorted_flows = sorted(tmp,          key=lambda x: x[1]['rate'])
        sorted_flows = sorted(sorted_flows, key=lambda x: x[1]['score'], reverse=True)
    
        for fl in sorted_flows:
            flow_id = fl[0]
            if flow_id in flows_assigned:
                continue
            flow_rate = fl[1]['rate']
            for k in self.queues:
                q_used = self.queues[k]['used']
                q_rate = self.queues[k]['rate']
                if total_rate + q_rate > self.bandwidth:
                    break
                if q_used == 0 and q_rate >= flow_rate:
                    self.flows[flow_id]['queue'] = k
                    self.queues[k]['used'] = 1
                    flows_assigned.append(flow_id)
                    total_rate = total_rate + q_rate
                    break


    # Add a classified flow into the flow dictionary.
    # Return the flowid of the classified flow, otherwise return None
    def add_flow(self, cflow):
        if cflow is not None:
            match = cflow['match']
            traffic_type = cflow['traffic_type']
            flow_id = cflow['flow_id']
            if flow_id is None:
                return None
            if traffic_type is not None:
                if flow_id not in self.flows:
                    self.flows[flow_id] = {'traffic_type': traffic_type, 'queue': 0,
                                           'match': match}
                    self.compute_optimal_assignment()
                return flow_id
        return None


    def remove_flow(self, flow_id):
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
