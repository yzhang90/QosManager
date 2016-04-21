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
        # Qos config
        self.qos_config = config.qos_config
        for k in self.qos_config:
            rec_rate = self.qos_config[k]['recommended']
            min_rate = self.qos_config[k]['minimum']
            self.qos_config[k]['recommended'] = utils.get_normalized_value(rec_rate)
            self.qos_config[k]['minimum']     = utils.get_normalized_value(min_rate)
        # Queue config
        queue_config = config.queue_config
        self.bandwidth = utils.get_normalized_value(queue_config['bandwidth'])
        self.queues = {}
        for k, v in queue_config['queues'].iteritems():
            self.queues[k] = {'rate': utils.get_normalized_value(v),'used': 0}
        # Flow table
        self.flow_table = {}
        self.counter = 0


    # Based on bandwith, queues and flows, compute the optimal assignment of 
    # classified flows to queues.
    def compute_optimal_assignment(self):
        total_rate = 0
        # First clear queue usage table
        for k in self.queues:
            self.queues[k]['used'] = 0
        # Second construct sorted list from the flows dictionary
        tmp = []
        flows_assigned = {}
        for k, v in self.flow_table.iteritems():
            score = self.qos_config[v['traffic_type']]['priority']
            rate = self.qos_config[v['traffic_type']]['recommended']
            seqid = v['id']
            criteria = {'score': score, 'rate': rate, 'id': seqid}
            tmp.append((k, criteria))

            score = self.qos_config[v['traffic_type']]['priority'] * 0.5
            rate = self.qos_config[v['traffic_type']]['minimum']
            seqid = v['id']
            criteria = {'score': score, 'rate': rate, 'id': seqid}
            tmp.append((k, criteria))

        sorted_flows = sorted(tmp,          key=lambda x: x[1]['id']) 
        sorted_flows = sorted(sorted_flows, key=lambda x: x[1]['rate'])
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
                    flows_assigned[flow_id] = k
                    self.queues[k]['used'] = 1
                    total_rate = total_rate + q_rate
                    break
        
        return flows_assigned


    # Update the flow table according to a flow assignment dict.
    # Send OFPFlowMod message if a flow table entry is updated.
    # An entry whose flow_id = 'flow_id' does not need to be handled here.
    def update_flow_table(self, datapath, flow_assign, flow_id=None):
        parser = datapath.ofproto_parser
  
        for k, v in self.flow_table.iteritems():
            changed = False
            if k in flow_assign:
                if flow_assign[k] != v['queue']:
                    self.flow_table[k]['queue'] = flow_assign[k]
                    changed = True
            else:
                if v['queue'] != 0:
                    self.flow_table[k]['queue'] = 0
                    changed = True

            if changed and k != flow_id:
                out_queue = self.flow_table[k]['queue']
                out_port = self.flow_table[k]['out_port']
                actions = [parser.OFPActionSetQueue(out_queue),
                           parser.OFPActionOutput(out_port)]
                match = parser.OFPMatch(**self.flow_table[k]['match'])
                utils.mod_flow_entry(datapath, match, actions)


    # Add a classified flow into the flow dictionary.
    # Return the flowid of the classified flow, otherwise return None
    def add_flow(self, datapath, cflow, out_port):
        if datapath.id != 1:
            return None
        if cflow is not None:
            match = cflow['match']
            traffic_type = cflow['traffic_type']
            flow_id = cflow['flow_id']
            if flow_id is None:
                return None
            if traffic_type is not None:
                if flow_id not in self.flow_table:
                    self.flow_table[flow_id] = {'traffic_type': traffic_type, 'out_port': out_port,
                                                'queue': 0, 'id': self.counter, 'match': match}
                    self.counter = self.counter + 1
                    result = self.compute_optimal_assignment()
                    self.update_flow_table(datapath, result, flow_id)
                return flow_id
        return None


    def remove_flow(self, datapath, flow_id):
        if datapath.id != 1:
            return None
        item = self.flow_table.pop(flow_id, None)
        if item:
            result = self.compute_optimal_assignment()
            self.update_flow_table(datapath, result, flow_id)

        
    def get_Actions(self, datapath, flow_id, in_port, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Qos Actions
        if flow_id is not None:
            # Only do traffic shaping at switch 1 port 4
            if datapath.id == 1 and out_port == 4:
                out_queue = self.flow_table[flow_id]['queue']
                actions = [parser.OFPActionSetQueue(out_queue),
                           parser.OFPActionOutput(out_port)]
            else:
                actions = [parser.OFPActionOutput(out_port)]
        # Normal Actions
        else:
            # Only do traffic shaping at switch 1 port 4
            if datapath.id == 1 and out_port == 4: 
                out_queue = 0
                actions = [parser.OFPActionSetQueue(out_queue),
                           parser.OFPActionOutput(out_port)]
            else:
                actions = [parser.OFPActionOutput(out_port)]

        return actions
