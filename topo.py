#!/usr/bin/env python

from mininet.cli  import CLI
from mininet.net  import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink 
from mininet.term import makeTerm

if '__main__' == __name__:
    net = Mininet(controller=RemoteController, link=TCLink)

    c0 = net.addController('c0', port=6633)

    s1 = net.addSwitch('s1')

    h1 = net.addHost('h1')
    h2 = net.addHost('h2')

    net.addLink(s1, h1, bw=500)
    net.addLink(s1, h2)

    net.build()
    c0.start()
    s1.start([c0])

    #net.startTerms()

    CLI(net)

    net.stop()
