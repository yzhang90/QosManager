sudo ovs-vsctl -- set Port s1-eth4 qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=8000000 queues=0=@q0,1=@q1,2=@q2,3=@q3,4=@q4,5=@q5,6=@q6,7=@q7,8=@q8,9=@q9,10=@q10,11=@q11 -- --id=@q0 create Queue other-config:max-rate=12000000 -- --id=@q1 create Queue other-config:min-rate=400000 other-config:max-rate=12000000 -- --id=@q2 create Queue other-config:min-rate=400000 other-config:max-rate=12000000 -- --id=@q3 create Queue other-config:min-rate=1000000 other-config:max-rate=12000000 -- --id=@q4 create Queue other-config:min-rate=1000000 other-config:max-rate=12000000 -- --id=@q5 create Queue other-config:min-rate=2000000 other-config:max-rate=12000000 -- --id=@q6 create Queue other-config:min-rate=2000000 other-config:max-rate=12000000 -- --id=@q7 create Queue other-config:min-rate=2000000 other-config:max-rate=12000000 -- --id=@q8 create Queue other-config:min-rate=3000000 other-config:max-rate=12000000 -- --id=@q9 create Queue other-config:min-rate=3000000 other-config:max-rate=12000000 -- --id=@q10 create Queue other-config:min-rate=5000000 other-config:max-rate=12000000 -- --id=@q11 create Queue other-config:min-rate=5000000 other-config:max-rate=12000000

sudo ovs-vsctl --all destroy qos
sudo ovs-vsctl --all destroy queue
sudo ovs-vsctl list Queue
sudo ovs-vsctl list Qos

tc qdisc show dev s1-eth4
tc class show dev s1-eth4
tc -s -d qdisc list dev s1-eth4
tc -s -d class list dev s1-eth4
