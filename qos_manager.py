"""
This is the main module of qos_switch
"""

import time

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

import qos_config
import qos_traffic
import qos_forwarding
import qos_control
import utils

class QosManager(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(QosManager, self).__init__(*args, **kwargs)
        self.hard_timeout = 10

        # Initialize modules
        self.config     = qos_config.QosConfig()
        self.tc         = qos_traffic.QosTraffic(self.config)
        self.forwarding = qos_forwarding.QosForwarding()
        self.control    = qos_control.QosControl(self.config)


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        utils.add_flow_entry(datapath, match, actions, priority=0)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        # Extract parameters
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt = packet.Packet(msg.data)
        pkt_eth = pkt.get_protocol(ethernet.ethernet)
        eth_type = pkt_eth.ethertype
        eth_src = pkt_eth.src
        eth_dst = pkt_eth.dst
        in_port = msg.match['in_port']

        is_ip_flow = False

        if eth_type == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        result = None
        # Only do the classificaion on IP packets
        if eth_type == ether_types.ETH_TYPE_IP:
            is_ip_flow = True
            result = self.tc.classify(pkt)

        out_port = self.forwarding.l2_switch(datapath, pkt, in_port)

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            if result:
                match = parser.OFPMatch(**result['match'])
            else:
                match = parser.OFPMatch(eth_src=eth_src, eth_dst=eth_dst, eth_type=eth_type)
            flow_id = self.control.add_flow(datapath, result, out_port)
            actions = self.control.get_Actions(datapath, flow_id, in_port, out_port)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                # only add idle_timeout to ip flows
                if is_ip_flow:
                    utils.add_flow_entry(datapath, match, actions, priority=1,
                                         buffer_id=msg.buffer_id, hard_timeout=self.hard_timeout)
                else:
                    utils.add_flow_entry(datapath, match, actions,
                                         priority=1, buffer_id=msg.buffer_id)
                return
            else:
                # only add idle_timeout to ip flows
                if is_ip_flow:
                    utils.add_flow_entry(datapath, match, actions,
                                         priority=1, hard_timeout=self.hard_timeout)
                else:
                    utils.add_flow_entry(datapath, match, actions, priority=1)

                data = msg.data
                out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                          in_port=in_port, actions=actions, data=data)
                datapath.send_msg(out)
        else:
            actions = self.control.get_Actions(datapath, None, in_port, out_port)
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data

            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)


    #@set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    #def _flow_removed_handler(self, ev):
        # Extract parameters
    #    msg = ev.msg
    #    print(msg)
    #    datapath = msg.datapath
    #    match = msg.match
    #    flow_id = utils.compute_flow_id2(match)
    #    self.tc.remove_flow(flow_id)
    #    self.control.remove_flow(datapath, flow_id)

