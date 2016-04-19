"""
Utility data, functions
"""

import re

from ryu.lib.packet import ethernet, ether_types
from ryu.lib.packet import ipv4, tcp, udp
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


# Given a packet, compute the hashcode of a flow based on five tuple.
# Update the match_dict if it is not None
def compute_flow_id1(pkt, match_dict=None):
    pkt_eth = pkt.get_protocol(ethernet.ethernet)
    if pkt_eth is None:
        return None
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

            if match_dict is not None:
                match_dict.update(tmp_dict)
            
            if ip_tuple:
                return hash(ip_tuple)
            else:
                return None
        else:
            return None
    else:
        return None

# Given a match dictionary, compute the hashcode of a flow 
# based on five tuple stored in the dictionary.
def compute_flow_id2(match_dict):
    eth_type = match_dict.get('eth_type')
    if eth_type == ether_types.ETH_TYPE_IP:
        ip_proto = match_dict.get('ip_proto')
        ipv4_src = match_dict.get('ipv4_src')
        ipv4_dst = match_dict.get('ipv4_dst')
        if ip_proto == inet.IPPROTO_TCP:
            tcp_src = match_dict.get('tcp_src')
            tcp_dst = match_dict.get('tcp_dst')
            ip_tuple = (ipv4_src, tcp_src, ipv4_dst, tcp_dst, ip_proto)
        elif ip_proto == inet.IPPROTO_UDP:
            udp_src = match_dict.get('udp_src')
            udp_dst = match_dict.get('udp_dst')
            ip_tuple = (ipv4_src, udp_src, ipv4_dst, udp_dst, ip_proto)
        else:
            return None

        return hash(ip_tuple)
    else:
        return None


def add_flow_entry(datapath, match, actions, **kwargs):
    ofproto      = datapath.ofproto
    parser       = datapath.ofproto_parser
    priority     = kwargs.setdefault('priority', 0)
    buffer_id    = kwargs.setdefault('buffer_id', None)
    idle_timeout = kwargs.setdefault('idle_timeout', 0)
    flags        = kwargs.setdefault('flags', ofproto.OFPFF_SEND_FLOW_REM)

    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)]
    if buffer_id:
        mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                priority=priority, match=match,
                                instructions=inst, idle_timeout=idle_timeout, flags=flags)
    else:
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst,
                                idle_timeout=idle_timeout, flags=flags)
    datapath.send_msg(mod)


def mod_flow_entry(datapath, match, actions):
    ofproto      = datapath.ofproto
    parser       = datapath.ofproto_parser
    
    inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                         actions)]
    mod = parser.OFPFlowMod(datapath=datapath, command=ofproto.OFPFC_MODIFY,
                            match=match, instructions=inst)
    print mod
    datapath.send_msg(mod)
