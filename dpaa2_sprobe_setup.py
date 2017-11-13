import re
from subprocess import check_output, check_call, CalledProcessError

# https://github.com/qoriq-open-source/dpdk-extras/blob/integration/dpaa2/dynamic_dpl.sh


class DPAA2_Obj():
    def __init__(self, dprc):
        self.dprc = dprc
        self.name = None

    def create(self):
        self.dprc.createObj(self, [], 1)

    def __repr__(self, indent=0):
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def exists(self):
        try:
            restool([self.__class__.__name__.lower(), "info", self.name])
            return True
        except CalledProcessError as e:
            return False


def restool(opts):
    return check_output(" ".join(["restool", "--script", ] + opts),
                        shell=True).strip()


def formatOptions(options):
    if options:
        return '--options="%s"' % (",".join(options))
    else:
        return ""


class DPBP(DPAA2_Obj):
    """
    DPAA2 Buffer pool
    """


class DPMAC(DPAA2_Obj):
    def __init__(self, dprc, _id):
        self.dprc = dprc
        self.id = _id
        self.name = "dpmac.%d" % _id

    def create(self):
        self.dprc.createObj(self, ["--mac-id=%d" % self.id], 1)


class DPCON(DPAA2_Obj):
    """
    DPAA2 Connection
    """

    def __init__(self, dprc, priorities=2):
        DPAA2_Obj.__init__(self, dprc)
        self.priorities = priorities

    def create(self):
        opts = ["--num-priorities=%d" % (self.priorities), ]
        self.dprc.createObj(self, opts, 1)


class DPIO(DPAA2_Obj):
    """
    DPAA2 I/O
    """

    def __init__(self, dprc, channel_mode="DPIO_LOCAL_CHANNEL",
                 priorities=1):
        DPAA2_Obj.__init__(self, dprc)
        self.channel_mode = channel_mode
        self.priorities = priorities

    def create(self):
        dprc = self.dprc
        opts = ["--channel-mode=%s" % (self.channel_mode),
                "--num-priorities=%d" % (self.priorities)]
        dprc.createObj(self, opts, 1)


class DPSW(DPAA2_Obj):
    """
    DPAA2 L2 switch
    """
    OPT_CTRL_IF_DIS = "DPSW_OPT_CTRL_IF_DIS"
    OPT_FLOODING_DIS = "DPSW_OPT_FLOODING_DIS"
    OPT_FLOODING_METERING_DIS = "DPSW_OPT_FLOODING_METERING_DIS"
    OPT_METERING_EN = "DPSW_OPT_METERING_EN"

    def __init__(self, dprc, intfsCnt, max_vlans=16,
                 max_fdbs=1, max_fdb_entries=1024, fdb_aging_time=300,
                 max_fdb_mc_groups=32, options=None, name=None):
        self.dprc = dprc
        self.name = name
        self.intfsCnt = intfsCnt
        self.max_vlans = max_vlans
        self.max_fdbs = max_fdbs
        self.max_fdb_entries = max_fdb_entries
        self.fdb_aging_time = fdb_aging_time
        self.max_fdb_mc_groups = max_fdb_mc_groups
        if options is None:
            options = [DPSW.OPT_CTRL_IF_DIS, ]
        self.options = options
        self.mcp = None
        self.bps = []

    def destroy(self):
        with open("/sys/bus/fsl-mc/drivers/vfio-fsl-mc/unbind", "w") as f:
            f.write(self.name + "\n")
        restool(["dpsw", "destroy", self.name])

    def create(self, pluged=1):
        rc = self.dprc
        self.mcp = rc.createDPMCP()
        if self.OPT_CTRL_IF_DIS not in self.options:
            bp = rc.createDPBP()
            self.bps.append(bp)

        options = [
            '--num-ifs=%d' % self.intfsCnt,
            '--max-vlans=%d' % self.max_vlans,
            '--max-fdbs=%d' % self.max_fdbs,
            '--max-fdb-entries=%d' % self.max_fdb_entries,
            '--fdb-aging-time=%d' % self.fdb_aging_time,
            '--max-fdb-mc-groups=%d' % self.max_fdb_mc_groups,
            formatOptions(self.options)
        ]

        rc.createObj(self, options, pluged)

        # change driver from vfio-fsl_mc to dpaa2_ethsw
        # try:
        #    with open("/sys/bus/fsl-mc/devices/" + self.name + "/driver/unbind", "w") as f:
        #        f.write(self.name + "\n")
        # except IOError:
        #    # not binded to any driver
        #    pass
        #
        # with open("/sys/bus/fsl-mc/drivers/dpaa2_ethsw/bind", "w") as f:
        #    f.write(self.name + "\n")

    def __getitem__(self, key):
        assert key < self.intfsCnt and key >= 0
        return DPSW_PORT(self, key)


class DPSW_PORT(DPAA2_Obj):
    def __init__(self, sw, portId):
        self.name = "%s.%d" % (sw.name, portId)


class DPMCP(DPAA2_Obj):
    """
    DPAA2 MC portal
    """


class DPNI(DPAA2_Obj):
    """
    DPAA2 network interface
    """
    OPT_TX_FRM_RELEASE = "DPNI_OPT_TX_FRM_RELEASE"
    OPT_NO_MAC_FILTER = "DPNI_OPT_NO_MAC_FILTER"
    OPT_HAS_POLICING = "DPNI_OPT_HAS_POLICING"
    OPT_SHARED_CONGESTION = "DPNI_OPT_SHARED_CONGESTION"
    OPT_HAS_KEY_MASKING = "DPNI_OPT_HAS_KEY_MASKING"
    OPT_NO_FS = "DPNI_OPT_NO_FS"

    def __init__(self, dprc, mac=None):
        DPAA2_Obj.__init__(self, dprc)
        self.options = []
        self.num_tcs = 8
        self.num_queues = 8
        self.fs_entries = 1
        self.vlan_entries = 16
        self.qos_entries = 64

    def setMAC(self, mac):
        return restool(["dpni", "update", self.name, "--mac-addr=%s" % mac])

    def create(self):
        rc = self.dprc
        rc.createDPBP()
        rc.createDPMCP()
        for _ in range(self.num_queues):
            rc.createDPCON()

        opts = [
            "--options=%s" % formatOptions(self.options),
            "--num-tcs=%d" % self.num_tcs,
            "--num-queues=%d" % self.num_queues,
            "--fs-entries=%d" % self.fs_entries,
            "--vlan-entries=%d" % self.vlan_entries,
            "--qos-entries=%d" % self.qos_entries,
        ]

        rc.createObj(self, opts, 1)


class DPCI(DPAA2_Obj):
    """
    The Datapath Communication Interface
    provides general purpose processing core software with a transport mechanism
    typically for control and configuration command interfaces to AIOP applications. The AIOP service layer implements the
    AIOP-side of the transport, but the commands are application-specific. Note that AIOP is optional in DPAA2 and is not present
    on some SoCs.
    """


class DPDMUX(DPAA2_Obj):
    METHOD_NONE = "DPDMUX_METHOD_NONE"
    METHOD_C_VLAN_MAC = "DPDMUX_METHOD_C_VLAN_MAC"
    METHOD_MAC = "DPDMUX_METHOD_MAC"
    METHOD_C_VLAN = "DPDMUX_METHOD_C_VLAN"
    MANIP_NONE = "DPDMUX_MANIP_NONE"
    MANIP_ADD_REMOVE_S_VLAN = "DPDMUX_MANIP_ADD_REMOVE_S_VLAN"
    OPT_BRIDGE_EN = "DPDMUX_OPT_BRIDGE_EN"

    def __init__(self, dprc):
        DPAA2_Obj.__init__(self, dprc)
        self.method = self.METHOD_MAC
        self.manip = self.MANIP_NONE
        # Number of virtual interfaces (excluding the uplink interface)
        self.num_ifs = 2
        # Max entries in DMux address table. Default is 64.
        self.max_dmat_entries = 64
        # Number of multicast groups in DMAT. Default is 32 groups.
        self.max_mc_groups = 32
        self.options = [self.OPT_BRIDGE_EN]

    def create(self):
        self.dprc.createDPMCP()
        opts = [
            '--num-ifs=%d' % self.num_ifs,
            formatOptions(self.options),
            "--method=%s" % self.method,
            "--max-dmat-entries=%d" % self.max_dmat_entries,
            "--max-mc-groups=%d" % self.max_mc_groups,
            "--manip=%s" % self.manip,
        ]
        self.dprc.createObj(self, opts, 1)

        # change driver from vfio-fsl_mc to dpaa2_ethsw
        # try:
        #    with open("/sys/bus/fsl-mc/devices/" + self.name + "/driver/unbind", "w") as f:
        #        f.write(self.name + "\n")
        # except IOError:
        #    # not binded to any driver
        #    pass
        #
        # with open("/sys/bus/fsl-mc/drivers/dpaa2_evb/bind", "w") as f:
        #    f.write(self.name + "\n")

    def __getitem__(self, key):
        assert key < self.num_ifs + 1 and key >= 0
        return DPDMUX_PORT(self, key)


class DPDMUX_PORT(DPAA2_Obj):
    def __init__(self, sw, portId):
        self.name = "%s.%d" % (sw.name, portId)


class DPRC(DPAA2_Obj):
    """
    DPAA2 Resource Container
    """

    OPT_SPAWN_ALLOWED = "DPRC_CFG_OPT_SPAWN_ALLOWED"
    OPT_ALLOC_ALLOWED = "DPRC_CFG_OPT_ALLOC_ALLOWED"
    OPT_OBJ_CREATE_ALLOWED = "DPRC_CFG_OPT_OBJ_CREATE_ALLOWED"
    OPT_TOPOLOGY_CHANGES_ALLOWED = "DPRC_CFG_OPT_TOPOLOGY_CHANGES_ALLOWED"
    OPT_IOMMU_BYPASS = "DPRC_CFG_OPT_IOMMU_BYPASS"
    OPT_AIOP = "DPRC_CFG_OPT_AIOP"
    OPT_IRQ_CFG_ALLOWED = "DPRC_CFG_OPT_IRQ_CFG_ALLOWED"
    INDENT_STEP = 2

    def __init__(self, dpaa2id, parent=None, label=None):
        self.name = "%s.%d" % (self.__class__.__name__.lower(), dpaa2id)
        self.label = label
        self.parent = parent
        self.children = []

    @classmethod
    def _list_parse(cls, obj_list):
        """
        @return: tuple (discovered objects, numer of taken items)
        """
        current_indent = 0
        top = current_obj = []
        stack = []
        prev = None

        while obj_list:
            obj_indent, dpaa2cls, index = obj_list.pop(0)
            if obj_indent == current_indent:
                pass

            elif obj_indent > current_indent:
                # we've gone down a level,
                # and then save the current ident
                # and block to the stack
                stack.insert(0, (current_indent, current_obj))
                current_indent = obj_indent
                current_obj = prev

            elif obj_indent < current_indent:
                # we've gone up one or more levels, pop the stack
                # until we find out which level and return to it
                found = False
                while stack:
                    parent_indent, parent_block = stack.pop(0)
                    if parent_indent == obj_indent:
                        found = True
                        break
                if not found:
                    raise Exception('indent not found in parent stack')
                current_indent = obj_indent
                current_obj = parent_block

            assert dpaa2cls == "dprc", repr(dpaa2cls)
            prev = DPRC(index)
            if isinstance(current_obj, list):
                current_obj.append(prev)
            else:
                current_obj.children.append(prev)
        return top

    @classmethod
    def list(cls):
        dprcs_list = restool(["dprc", "list"])
        r = re.compile("^(\s*)(\S+)\.(\d+)")

        def parseLine(line):
            m = r.match(line)
            indent = len(m.group(1))
            dpaa2cls = m.group(2)
            index = int(m.group(3))
            return indent, dpaa2cls, index

        dprcs_list = list(map(parseLine,  dprcs_list.split('\n')))
        return cls._list_parse(dprcs_list)

    def createDPRC(self, options=None):
        """
        Create resource container in this resource container
        """
        if options is None:
            # default options
            options = [self.OPT_SPAWN_ALLOWED,
                       self.OPT_ALLOC_ALLOWED,
                       self.OPT_OBJ_CREATE_ALLOWED]

        cmd = ["dprc",
               "create",
               self.name,
               formatOptions(options)]

        if self.label:
            cmd.append('--label="%s"' % self.label)
        dpaa2id = restool(cmd)
        match = re.search("\S*\.(\d+)", dpaa2id)
        dpaa2id = int(match.groups(1)[0])
        rc = DPRC(dpaa2id, parent=self)
        self.sync()
        rc.sync()
        return rc

    def createDPNI(self):
        ni = DPNI(self)
        ni.create()
        return ni

    def createDPBP(self):
        bp = DPBP(self)
        bp.create()
        return bp

    def createDPMCP(self):
        dpmcp = DPMCP(self)
        dpmcp.create()
        return dpmcp

    def createDPMAC(self, macId):
        self.createDPMCP()
        mac = DPMAC(self, macId)
        #self.assign(mac, 1)
        return mac

    def createDPIO(self):
        io = DPIO(self)
        io.create()
        return io

    def createDPSW(self, intfsCnt):
        sw = DPSW(self, intfsCnt)
        sw.create(1)
        return sw

    def createDPDMUX(self, intfsCnt):
        mux = DPDMUX(self)
        mux.num_ifs = intfsCnt
        mux.create()
        return mux

    def createDPCI(self):
        ci = DPCI()
        ci.create()
        return ci

    def createDPCON(self):
        con = DPCON(self)
        con.create()
        return con

    @classmethod
    def sync(cls):
        check_call(["restool", "dprc", "sync"])

    def createObj(self, obj, opts, plugged):
        """
        Physicaly create dpaa2 object inside this container

        @param obj: DPAA2 object which is not instanciated in this RC
        @param opts: list of cli options for restool
        @param plugged: int which desc

        @return: obj - dpaa2 object physicaly instanciated
            inside of this resource container
        """
        obj.name = restool([obj.__class__.__name__.lower(),
                            "create"] + opts
                           + ["--container=%s" % self.name])
        self.sync()
        self.assign(obj, plugged)

        assert obj.exists(), obj.name

        return obj

    def assign(self, obj, plugged, parent=None):
        if parent is None:
            parent = self
        cmd = ["dprc", "assign", parent.name,
               "--object=" + obj.name, "--child=" + self.name,
               "--plugged=" + str(plugged)
               ]
        restool(cmd)
        self.sync()
        self.children.append(obj)

    def unassign(self, obj, parent=None):
        if parent is None:
            parent = self
        cmd = ["dprc", "unassign", parent.name,
               "--object=" + obj.name, "--child=" + self.name,
               ]
        restool(cmd)
        self.children.remove(obj)
        self.sync()

    def destroy(self):
        # dpaa2 destroys children automatically
        try:
            with open("/sys/bus/fsl-mc/drivers/vfio-fsl-mc/unbind", "w") as f:
                f.write(self.name + "\n")
        except IOError:
            # not binded
            pass

        restool(["dprc", "destroy", self.name])
        self.sync()

    def show(self, resType=None):
        if resType is None:
            res = "--resources"
        else:
            res = "--resource-type=%s" % resType.__name__.lower()

        return restool([self.name, res])

    def info(self, verbose=False):
        cmd = [self.name]
        if verbose:
            cmd.append("--verbose")

        return restool(cmd)

    def connect(self, obj0, obj1):
        self.createDPCON()
        cmd = ["dprc", "connect", self.name,
               "--endpoint1=" + obj0.name,
               "--endpoint2=" + obj1.name]
        restool(cmd)
        self.sync()

    def disconnect(self, obj):
        cmd = ["dprc", "disconnect", self.name,
               "--endpoint=" + obj.name]
        restool(cmd)
        self.sync()

    def _getIndent(self, indent):
        return "    " * indent

    def __repr__(self, indent=0):
        children = [ch.__repr__(indent=indent + 1)
                    for ch in self.children]
        myIndent = self._getIndent(indent)
        if children:
            children = children = ",\n".join(children)
            return "%s<DPRC %s, children:[\n%s]>" % (myIndent,
                                                     self.name,
                                                     children)
        else:
            return "%s<DPRC %s>" % (myIndent, self.name)

# DPDMUX/DPSW is created in root because we need to keep it
# from driver vfio override


def sprobe_dmux(root):
    dprc = root.createDPRC()
    mcp = dprc.createDPMCP()
    for _ in range(16):
        dprc.createDPIO()

    for _ in range(16):
        dprc.createDPBP()

    PORTS = [1, 2, 3, 4]

    dmux = root.createDPDMUX(len(PORTS))
    for i, portId in enumerate(PORTS):
        mac = dprc.createDPMAC(portId)
        root.connect(dmux[i + 1], mac)

    ni = DPNI(dprc)
    ni.num_tcs = 4
    ni.num_queues = 4
    ni.create()
    ni.setMAC("00:00:00:00:00:0%d" % 1)
    root.connect(ni, dmux[0])
    return dprc


def sprobe_sw(root):
    dprc = root.createDPRC()
    mcp = dprc.createDPMCP()
    for _ in range(16):
        dprc.createDPIO()

    for _ in range(16):
        dprc.createDPBP()

    PORTS = [1, 2, 3, 4]
    NI_CNT = 2

    for _ in range(32):
        dprc.createDPCON()

    sw = root.createDPSW(len(PORTS) + NI_CNT)
    for i, portId in enumerate(PORTS):
        mac = dprc.createDPMAC(portId)
        root.connect(sw[i], mac)

    for i in range(NI_CNT):
        ni = dprc.createDPNI()
        ni.setMAC("00:00:00:00:00:0%d" % i)
        root.connect(ni, sw[len(PORTS) + i])

    return dprc


if __name__ == "__main__":
    root = DPRC.list()[0]
    with open("/sys/module/vfio_iommu_type1/parameters/allow_unsafe_interrupts", "w") as f:
        f.write("1\n")

    # let only root dprc
    for dprc in root.children:
        dprc.destroy()

    # dprc = sprobe_sw(root)
    dprc = sprobe_dmux(root)

    with open("/sys/bus/fsl-mc/devices/" + dprc.name + "/driver_override", "w") as f:
        f.write("vfio-fsl-mc\n")

    try:
        with open("/sys/bus/fsl-mc/drivers/vfio-fsl-mc/bind", "w") as f:
            f.write(dprc.name + "\n")
    except IOError:
        pass

    print(dprc)
