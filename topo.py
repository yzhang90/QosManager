#!/usr/bin/python

import subprocess

from mininet.cli  import CLI
from mininet.net  import Mininet
from mininet.node import RemoteController, OVSHtbSwitch
from mininet.link import TCLink 

if __name__  == '__main__':
    
    #Clean qos and queues
    cmd = "sudo ovs-vsctl show"
    subprocess.call(cmd, shell=True)
    cmd = "sudo ovs-vsctl --all destroy qos"
    subprocess.call(cmd, shell=True)
    cmd = "sudo ovs-vsctl --all destroy queue"
    subprocess.call(cmd, shell=True)
    

    net = Mininet(switch=OVSHtbSwitch, controller=RemoteController, link=TCLink)

    c0 = net.addController('c0', port=6633)

    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')

    hs1 = net.addHost('hs1')
    hs2 = net.addHost('hs2')
    hs3 = net.addHost('hs3')

    hc1 = net.addHost('hc1')
    hc2 = net.addHost('hc2')
    hc3 = net.addHost('hc3')

    net.addLink(hs1, s1)
    net.addLink(hs2, s1)
    net.addLink(hs3, s1)

    net.addLink(s1, s2, bw=8)

    net.addLink(hc1, s2)
    net.addLink(hc2, s2)
    net.addLink(hc3, s2)

    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])

    #net.startTerms()

    CLI(net)

    net.stop()
