sudo ovs-vsctl -- set Port s1-eth4 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=8000000 queues=0=@q0,1=@q1,2=@q2,3=@q3,4=@q4,5=@q5,6=@q6 -- --id=@q0 create Queue other-config:max-rate=8000000 -- --id=@q1 create Queue other-config:min-rate=100000 other-config:max-rate=8000000 -- --id=@q2 create Queue other-config:min-rate=300000 other-config:max-rate=8000000 -- --id=@q3 create Queue other-config:min-rate=512000 other-config:max-rate=8000000 -- --id=@q4 create Queue other-config:min-rate=1000000 other-config:max-rate=8000000 -- --id=@q5 create Queue other-config:min-rate=1500000 other-config:max-rate=8000000 -- --id=@q6 create Queue other-config:min-rate=5000000 other-config:max-rate=8000000

sudo ovs-vsctl --all destroy qos
sudo ovs-vsctl --all destroy queue
sudo ovs-vsctl list Queue
sudo ovs-vsctl list Qos

tc qdisc show dev s1-eth4
tc class show dev s1-eth4
tc -s -d qdisc list dev s1-eth4
tc -s -d class list dev s1-eth4
