sudo ovs-vsctl -- set Port s1-eth4 qos=0=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create Queue other-config:min-rate=3000000 other-config:max-rate=10000000 -- --id=@q1 create Queue other-config:min-rate=5000000 other-config:max-rate=10000000 -- --id=@q2 create Queue other-config:min-rate=7000000 other-config:max-rate=10000000

sudo ovs-vsctl --all destroy qos
sudo ovs-vsctl --all destroy queue
sudo ovs-vsctl list Queue
sudo ovs-vsctl list Qos

tc qdisc show dev s1-eth4
tc class show dev s1-eth4
tc -s -d qdisc list dev s1-eth4
tc -s -d class list dev s1-eth4
