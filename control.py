"""
This module provides methods for Qos control.
"""

import logging


class QosControl(object):
    
    def __init__(self):
        super(QosControl, self).__init__()

    def computeNormalActions(self, datapath, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        actions = [parser.OFPActionOutput(out_port)]

        return actions

    def computeQosActions(self, datapath, in_port, out_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if datapath.id == 1 and out_port == 4 and in_port == 1:
            out_queue = 1
            actions = [parser.OFPActionSetQueue(out_queue),
                        parser.OFPActionOutput(out_port)]
        else:
            actions = [parser.OFPActionOutput(out_port)]

        return actions

