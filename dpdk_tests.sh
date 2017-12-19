#
# Lets suggest we would like to run looback test from testpmd app from DPDK
# testpmd -c 3 -n 1 -- -i --nb-cores=1 --nb-ports=4 --total-num-mbufs=1025 --forward-mode=txonly --disable-hw-vlan --port-topology=chained --no-flush-rx -a
# https://software.intel.com/en-us/articles/testing-dpdk-performance-and-features-with-testpmd
# http://fast.dpdk.org/doc/pdf-guides/testpmd_app_ug-17.08.pdf

# 1)
# http://dpdk.org/doc/guides/linux_gsg/sys_reqs.html
# mount hugepages
mkdir /mnt/huge
mount -t hugetlbfs nodev /mnt/huge

#
# Otherwise:
#
# EAL: Detected 8 lcore(s)
# EAL: 256 hugepages of size 2097152 reserved, but no mounted hugetlbfs found for that size
# PANIC in rte_eal_init():
# Cannot get hugepage information
#
#

# 2) allocate interfaces/mac/dpaa2 resource container
# https://www.nxp.com/docs/en/supporting-information/QORIQ_ODP_v16.08_REV0.pdf  + ctrl+f dynamic_dpl.sh
source /usr/odp/scripts/dynamic_dpl.sh dpmac.1 dpmac.2 dpmac.3 dpmac.4
# (= allocate SFP+ ports eth4-7)
# (interfaces 5-8 are cooper ports on right side, and they are named eth0-3)
#
# Otherwise:
#
# EAL: Detected 8 lcore(s)
# EAL: Probing VFIO support...
# EAL: VFIO support initialized
# EAL: cannot open /proc/self/numa_maps, consider that all memory is in socket_id 0
# EAL: dpaa2_setup_vfio_grp():  VFIO container not set in env DPRC
# EAL: rte_eal_dpaa2_init(): DPAA2: Unable to setup VFIO
# EAL: Cannot init FSL_DPAA2 SCAN
# EAL: setup_dmamap():  Container is not connected yet.
# PMD: DPAA2: Unable to DMA Map devicesPMD: bnxt_rte_pmd_init() called for (null)
# EAL: PCI device 0000:01:00.0 on NUMA socket 0
# EAL:   probe driver: 8086:10d3 rte_em_pmd
# EAL: No probed ethernet devices
# Interactive-mode selected
# EAL: Error - exiting with code: 1
#   Cause: Invalid port 4
#

# to undo this step there is (where dprc.1 is name of your resource container
# you have created in previous step)
# source /usr/odp/scripts/destroy_dynamic_dpl.sh dprc.1



# 3) now run 
testpmd -- --interactive
# and write 
show port info all
# and check required ports are present

# you should see:


# root@ls2088ardb:~# testpmd -- --interactive
# EAL: Detected 8 [  162.295496] Bits 55-60 of /proc/PID/pagemap entries are about to stop being page-shift some time soon. See the linux/Documentation/vm/pagemap.txt for details.
# lcore(s)
# EAL: Probing VFIO support...
# EAL: VFIO support initialized
# EAL: cannot open /proc/self/numa_maps, consider that all memory is in socket_id 0
# PMD: DPAA2: Processing Container = dprc.2
# PMD: Total devices in container = 39, MCP ID = 21
# 
# ########## Detected NXP LS208x with Cortex-A72
# PMD: DPAA2: Added [dpseci-0]
# PMD: DPAA2: Added [dpni-1]
# PMD: DPAA2: Added [dpni-2]
# PMD: DPAA2: Added [dpni-3]
# PMD: DPAA2: Added [dpni-4]
# PMD: DPAA2: Added [dpni-5]
# PMD: DPAA2: Added dpbp_count = 4 dpio_count=10
# PMD: DPAA2: Device setup completed
# PMD: DPAA2: Devices DMA mapped successfully
# PMD: bnxt_rte_pmd_init() called for (null)
# EAL: PCI device 0000:01:00.0 on NUMA socket 0
# EAL:   probe driver: 8086:10d3 rte_em_pmd
# EAL: PCI device 0000:00:00.3 on NUMA socket 0
# EAL:   probe driver: 1957:3 rte_dpaa2_sec_pmd
# EAL: PCI device 0000:00:01.7 on NUMA socket 0
# EAL:   probe driver: 1957:7 rte_dpaa2_dpni
# EAL: PCI device 0000:00:02.7 on NUMA socket 0
# EAL:   probe driver: 1957:7 rte_dpaa2_dpni
# EAL: PCI device 0000:00:03.7 on NUMA socket 0
# EAL:   probe driver: 1957:7 rte_dpaa2_dpni
# EAL: PCI device 0000:00:04.7 on NUMA socket 0
# EAL:   probe driver: 1957:7 rte_dpaa2_dpni
# EAL: PCI device 0000:00:05.7 on NUMA socket 0
# EAL:   probe driver: 1957:7 rte_dpaa2_dpni
# Interactive-mode selected
# USER1: create a new mbuf pool <mbuf_pool_socket_0>: n=203456, size=2304, socket=0
# 
# Warning! Cannot handle an odd number of ports with the current port topology. Configuration must be changed to have an even number of ports, or relaunch application with --port-topology=chained
# 
# Configuring Port 0 (socket 0)
# Port 0: 00:00:00:00:00:01
# Configuring Port 1 (socket 0)
# Port 1: 00:00:00:00:00:02
# Configuring Port 2 (socket 0)
# Port 2: 00:00:00:00:00:03
# Configuring Port 3 (socket 0)
# Port 3: 00:00:00:00:00:04
# Configuring Port 4 (socket 0)
# Port 4: 00:00:00:11:11:11
# Checking link statuses...
# Port 0 Link Up - speed 10000 Mbps - full-duplex
# Port 1 Link Up - speed 10000 Mbps - full-duplex
# Port 2 Link Up - speed 10000 Mbps - full-duplex
# Port 3 Link Up - speed 10000 Mbps - full-duplex
# Port 4 Link Up - speed 0 Mbps - half-duplex
# 
# Done
# testpmd> show port info all
# 
# ********************* Infos for port 0  *********************
# MAC address: 00:00:00:00:00:01
# Connect to socket: 0
# memory allocation on the socket: 0
# Link status: up
# Link speed: 10000 Mbps
# Link duplex: full-duplex
# Promiscuous mode: enabled
# Allmulticast mode: disabled
# Maximum number of MAC addresses: 16
# Maximum number of MAC addresses of hash filtering: 0
# VLAN offload: 
#   strip on 
#   filter on 
#   qinq(extend) off 
# No flow type is supported.
# Max possible RX queues: 8
# Max possible number of RXDs per queue: 65535
# Min possible number of RXDs per queue: 0
# RXDs number alignment: 1
# Max possible TX queues: 8
# Max possible number of TXDs per queue: 65535
# Min possible number of TXDs per queue: 0
# TXDs number alignment: 1
# 
# ********************* Infos for port 1  *********************
# MAC address: 00:00:00:00:00:02
# Connect to socket: 0
# memory allocation on the socket: 0
# Link status: up
# Link speed: 10000 Mbps
# Link duplex: full-duplex
# Promiscuous mode: enabled
# Allmulticast mode: disabled
# Maximum number of MAC addresses: 16
# Maximum number of MAC addresses of hash filtering: 0
# VLAN offload: 
#   strip on 
#   filter on 
#   qinq(extend) off 
# No flow type is supported.
# Max possible RX queues: 8
# Max possible number of RXDs per queue: 65535
# Min possible number of RXDs per queue: 0
# RXDs number alignment: 1
# Max possible TX queues: 8
# Max possible number of TXDs per queue: 65535
# Min possible number of TXDs per queue: 0
# TXDs number alignment: 1
# 
# ********************* Infos for port 2  *********************
# MAC address: 00:00:00:00:00:03
# Connect to socket: 0
# memory allocation on the socket: 0
# Link status: up
# Link speed: 10000 Mbps
# Link duplex: full-duplex
# Promiscuous mode: enabled
# Allmulticast mode: disabled
# Maximum number of MAC addresses: 16
# Maximum number of MAC addresses of hash filtering: 0
# VLAN offload: 
#   strip on 
#   filter on 
#   qinq(extend) off 
# No flow type is supported.
# Max possible RX queues: 8
# Max possible number of RXDs per queue: 65535
# Min possible number of RXDs per queue: 0
# RXDs number alignment: 1
# Max possible TX queues: 8
# Max possible number of TXDs per queue: 65535
# Min possible number of TXDs per queue: 0
# TXDs number alignment: 1
# 
# ********************* Infos for port 3  *********************
# MAC address: 00:00:00:00:00:04
# Connect to socket: 0
# memory allocation on the socket: 0
# Link status: up
# Link speed: 10000 Mbps
# Link duplex: full-duplex
# Promiscuous mode: enabled
# Allmulticast mode: disabled
# Maximum number of MAC addresses: 16
# Maximum number of MAC addresses of hash filtering: 0
# VLAN offload: 
#   strip on 
#   filter on 
#   qinq(extend) off 
# No flow type is supported.
# Max possible RX queues: 8
# Max possible number of RXDs per queue: 65535
# Min possible number of RXDs per queue: 0
# RXDs number alignment: 1
# Max possible TX queues: 8
# Max possible number of TXDs per queue: 65535
# Min possible number of TXDs per queue: 0
# TXDs number alignment: 1
# 
# ********************* Infos for port 4  *********************
# MAC address: 00:00:00:11:11:11
# Connect to socket: 0
# memory allocation on the socket: 0
# Link status: up
# Link speed: 0 Mbps
# Link duplex: half-duplex
# Promiscuous mode: enabled
# Allmulticast mode: disabled
# Maximum number of MAC addresses: 16
# Maximum number of MAC addresses of hash filtering: 0
# VLAN offload: 
#   strip on 
#   filter on 
#   qinq(extend) off 
# No flow type is supported.
# Max possible RX queues: 8
# Max possible number of RXDs per queue: 65535
# Min possible number of RXDs per queue: 0
# RXDs number alignment: 1
# Max possible TX queues: 8
# Max possible number of TXDs per queue: 65535
# Min possible number of TXDs per queue: 0
# TXDs number alignment: 1
# testpmd> 


# if you try http://fast.dpdk.org/doc/pdf-guides/testpmd_app_ug-17.08.pdf 4.5.11 with portlist 0,1,2,3
testpmd -l 0-8 -n 8  -- --rxq=8 --txq=8 --nb-cores=7 -i
set portmask 3
set coremask 6
set portlist 0,1
set txpkts 128
set burst 256
start tx_first
show port stats all
stop



