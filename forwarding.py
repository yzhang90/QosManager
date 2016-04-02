"""
This module provides methods for forwarding functions. 
"""

import logging 

from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

LOG = logging.getLogger(__name__)

class QosForwarding(object):

    def __init__(self):
        # mapping from mac to port for switching
        self.mac_to_port = {}
        self.propagate = False

    def l2_switch(self, datapath, eth, in_port):
        dpid = datapath.id
        ofproto = datapath.ofproto
        eth_src = eth.src
        eth_dst = eth.dst

        LOG.info("PacketIn dpid: %s, src: %s, dst: %s, in_port: %s",
                  dpid, eth_src, eth_dst, in_port)

        self.mac_to_port.setdefault(dpid, {})
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][eth_src] = in_port
        
        # check if dst MAC is in MAC table
        if eth_dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][eth_dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        
        return out_port
