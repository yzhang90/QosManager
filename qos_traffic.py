"""
This module provides methods for traffic classification.
"""

import logging

from ryu.lib.packet import ethernet, ether_types
from ryu.lib.packet import ipv4, tcp, udp
from ryu.lib.packet import in_proto as inet

import qos_config
import utils


class QosTraffic(object):

    def __init__(self, config):
        super(QosTraffic, self).__init__()
        traffic_config = config.traffic_config
        self.classifier = {}
        self.flows = {}
        id = 1
        for k, v in traffic_config.iteritems():
            for item in v:
                item['traffic_type'] = k
                self.classifier[id] = item
                id = id + 1

    def classify(self, pkt):
        pkt_eth = pkt.get_protocol(ethernet.ethernet)
        result = {'flow_id': None, 'match': {},
                  'traffic_type': None }

        #Get basic information from each flow
        #Important! eth_type is required!
        match = result['match']
        match['eth_type'] = pkt_eth.ethertype
        match['eth_src']  = pkt_eth.src
        match['eth_dst']  = pkt_eth.dst
        
        flow_id = utils.compute_flow_id1(pkt, match)

        if flow_id is None:
            return None

        if flow_id in self.flows:
            #flow_id is already in the map, no need to classify this flow.
            return self.flows[flow_id]
        else:
            result['flow_id'] = flow_id
            
 
        # Traffic Classification
        for item in self.classifier.itervalues():
            if 'protocol' in item:
                ip_proto = match['ip_proto']
                if item['protocol'] == 'tcp' and ip_proto != inet.IPPROTO_TCP:
                    continue
                if item['protocol'] == 'udp' and ip_proto != inet.IPPROTO_UDP:
                    continue

            if 'ipv4' in item:
                et = match['eth_type']
                ipv4_value = item['ipv4']
                if et == ether_types.ETH_TYPE_IP:
                    if 'src' in ipv4_value:
                        ipv4_src = match['ipv4_src']
                        if ipv4_value['src'] != ipv4_src:
                            continue
                    if 'dst' in ipv4_value:
                        ipv4_dst = match['ipv4_dst']
                        if ipv4_value['dst'] != ipv4_dst:
                            continue 
                else:
                    continue

            result['traffic_type'] = item['traffic_type']
            #bookkeep the classified result
            self.flows[flow_id] = result 
            return result

        #bookkeep the classified result
        self.flows[flow_id] = result
        return result
    

    def remove_flow(self, flowid):
        self.flows.pop(flowid, None)
