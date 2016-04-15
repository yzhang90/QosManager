"""
This module provides methods for traffic classification.
"""

import logging

from ryu.lib.packet import ethernet, ether_types
from ryu.lib.packet import ipv4, tcp, udp
from ryu.lib.packet import in_proto as inet

import qos_config

# Compute the hashcode of a flow based on five tuple. Update the match_dict if not None
def compute_flow_id(pkt, match_dict=None):
    pkt_eth = pkt.get_protocol(ethernet.ethernet)
    if pkt_eth.ethertype == ether_types.ETH_TYPE_IP:
        tmp_dict = {}
        pkt_ip4 = pkt.get_protocol(ipv4.ipv4)
        if pkt_ip4 is not None:
            tmp_dict['ip_proto'] = pkt_ip4.proto
            tmp_dict['ipv4_src'] = pkt_ip4.src
            tmp_dict['ipv4_dst'] = pkt_ip4.dst
            ip_tuple = None
            if pkt_ip4.proto == inet.IPPROTO_TCP:
                pkt_tcp = pkt.get_protocol(tcp.tcp)
                if pkt_tcp is not None:
                    tmp_dict['tcp_src'] = pkt_tcp.src_port
                    tmp_dict['tcp_dst'] = pkt_tcp.dst_port
                    ip_tuple = (tmp_dict['ipv4_src'], tmp_dict['tcp_src'],
                                tmp_dict['ipv4_dst'], tmp_dict['tcp_dst'], tmp_dict['ip_proto'])
                else:
                    return None
            elif pkt_ip4.proto == inet.IPPROTO_UDP:
                pkt_udp = pkt.get_protocol(udp.udp)
                if pkt_udp is not None:
                    tmp_dict['udp_src'] = pkt_udp.src_port
                    tmp_dict['udp_dst'] = pkt_udp.dst_port
                    ip_tuple = (tmp_dict['ipv4_src'], tmp_dict['udp_src'],
                                tmp_dict['ipv4_dst'], tmp_dict['udp_dst'], tmp_dict['ip_proto'])
                else:
                    return None
            else:
                return None

            if match_dict is not None:
                match_dict.update(tmp_dict)
            
            return hash(ip_tuple)

        else:
            return None
    else:
        return None


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
        
        flow_id = compute_flow_id(pkt, match)
        if flow_id in self.flows:
            #flow_id is already in the map, no need to classify this flow.
            return self.flows[flow_id]
        else:
            result['flow_id'] = flow_id
            
 
        # Traffic Classification
        for item in self.classifier.itervalues():
            if 'protocol' in item:
                ip_proto = match.get('ip_proto')
                if ip_proto is not None:
                    if item['protocol'] == 'tcp' and ip_proto != inet.IPPROTO_TCP:
                        continue
                    if item['protocol'] == 'udp' and ip_proto != inet.IPPROTO_UDP:
                        continue
                else:
                    continue

            if 'ipv4' in item:
                et = match.get('eth_type')
                ipv4_value = item['ipv4']
                if et == ether_types.ETH_TYPE_IP:
                    if 'src' in ipv4_value:
                        ipv4_src = match.get('ipv4_src')
                        if not (ipv4_src and ipv4_value['src'] == ipv4_src):
                            continue
                    if 'dst' in ipv4_value:
                        ipv4_dst = match.get('ipv4_dst')
                        if not (ipv4_dst and ipv4_value['dst'] == ipv4_dst):
                            continue 
                else:
                    continue

            result['traffic_type'] = item['traffic_type']
            #bookkeep the classified result
            if result['flow_id'] is not None:
                flow_id = result['flow_id']
                self.flows[flow_id] = result 
            return result

        #bookkeep the classified result
        if result['flow_id'] is not None:
            flow_id = result['flow_id']
            self.flows[flow_id] = result
        return result
    

    def remove_flow(self, pkt):
        flow_id = compute_flow_id(pkt)
