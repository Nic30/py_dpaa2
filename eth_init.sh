# after boot
# ip a
# 1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default 
#     link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
#     inet 127.0.0.1/8 scope host lo
#        valid_lft forever preferred_lft forever
#     inet6 ::1/128 scope host 
#        valid_lft forever preferred_lft forever
# 2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
#     link/ether 68:05:ca:44:5c:ce brd ff:ff:ff:ff:ff:ff
#     inet 192.168.0.201/24 scope global eth0
#        valid_lft forever preferred_lft forever
#     inet6 fe80::6a05:caff:fe44:5cce/64 scope link tentative 
#        valid_lft forever preferred_lft forever
# 3: ni0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
#     link/ether 42:bd:78:d2:f8:48 brd ff:ff:ff:ff:ff:ff
# 4: sit0@NONE: <NOARP> mtu 1480 qdisc noop state DOWN group default 
#     link/sit 0.0.0.0 brd 0.0.0.0



ip link set eth0 up
ip addr add 192.168.0.201/24 dev eth0
# non set mac address = non workin ni

#ip link set ni0 up
#ip addr add 192.168.1.4/24 dev ni0

mkdir /mnt/huge
mount -t hugetlbfs nodev /mnt/huge

export DPRC=dprc.2


cp ls-main ls-addsw
cp ls-main ls-addni
chmod +x ls-addni
chmod +x ls-addsw

function add_1ni() {
	ls-addni dpmac.1 --mac-addr=80:85:C2:21:06:39
}

function add_sw_1ni_1sfp () {
	# 1 ni, 1 sfp
	ls-addni -n
	# ni0 is lost, use ni1
	ls-addsw -i=2 dpni.1 dpmac.1
	ip link set ni1 down
	ip link set ni1 down
	ip link set sw0p1 down
	# manyally plug unplug, transceiver, they can be in UNKNOWN state
	ip link set sw0p1 up
	ip link set ni1 up
	ip addr add 192.168.1.4/24 dev ni1
	# now ping works
}

function add_sw_1ni_4sfp () {
	# 1ni, 4 sfp
	ls-addni -n
	# ni0 is lost, use ni1
	ls-addsw -i=5 dpni.1 dpmac.1 dpmac.2 dpmac.3 dpmac.4
	ip link set ni1 down
	ip link set sw0p1 down
	ip link set sw0p2 down
	ip link set sw0p3 down
	ip link set sw0p4 down
	# manyally plug unplug, transceiver, they can be in UNKNOWN state
	ip link set sw0p1 up
	ip link set sw0p2 up
	ip link set sw0p3 up
	ip link set sw0p4 up
	ip link set ni1 up
	# sw0 in UNKNOWN state somehow, but packets are flowing
	ip addr add 192.168.1.4/24 dev ni1
	# now ping works
}


