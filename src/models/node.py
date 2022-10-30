from typing import Optional, Any, List

from pydantic import BaseModel

from .report import NodeReport
from .vm import PVEVm


class DigestData(BaseModel):
    digest: str
    data: str


class NodeRootfs(BaseModel):
    total: int
    avail: int
    used: int
    free: int


class NodeMemory(BaseModel):
    total: int
    used: int
    free: int


class NodeSwap(NodeMemory):
    pass


class NodeCpuInfo(BaseModel):
    model: str
    sockets: int
    cores: int
    cpus: int
    mhz: str
    hvm: str
    user_hz: str
    flags: str


class NodeStatus(BaseModel):
    uptime: int
    wait: int
    idle: int
    rootfs: NodeRootfs
    pveversion: str
    ksm: dict
    loadavg: List[str]
    memory: NodeMemory
    kversion: str
    cpu: int
    cpuinfo: NodeCpuInfo
    swap: NodeSwap


class NodeDisk(BaseModel):
    type: str
    size: int
    health: str
    serial: str
    model: str
    mount: bool = False
    gpt: bool
    used: str
    vendor: str
    wearout: int
    wwn: str
    rpm: int
    osdid: int
    devpath: str
    by_id_link: str


class NodeTime(BaseModel):
    time: int
    localtime: int
    timezone: str


class NodeNetStats(BaseModel):
    vmid: str
    dev: str
    net_in: str
    net_out: str


class PVENode(BaseModel):
    id: str
    node: str
    type: str
    status: str
    uptime: str
    maxcpu: int
    maxmem: int
    maxdisk: int
    cpu: float
    mem: int
    disk: int
    ssl_fingerprint: str
    level: str
    client: Optional[Any]

    def get_containers(self):
        """获取节点的 LXC 容器信息 https://linuxcontainers.org/"""
        pass

    def get_vms(self):
        """获取节点的 QEMU 虚拟机信息"""
        vms = self.client.http_request('GET', f'/nodes/{self.node}/qemu')
        vms = [{**v, **{'client': self.client, 'node': self}} for v in vms]
        return [PVEVm(**vm) for vm in sorted(vms, key=lambda v: v.get('vmid', 0))]

    def get_status(self):
        """获取节点的状态"""
        data = self.client.http_request('GET', f'/nodes/{self.node}/status')
        return NodeStatus(**data)

    def get_disks(self) -> List[NodeDisk]:
        """获取节点的硬盘信息"""
        data = self.client.http_request('GET', f'/nodes/{self.node}/disks/list')
        result = []
        for disk in data:
            disk['mount'] = disk.get('mount', False)
            disk['gpt'] = disk['gpt'] == 1
            result.append(NodeDisk(**disk))
        return result

    def get_time(self):
        """获取节点的时间或时区信息"""
        data = self.client.http_request('GET', f'/nodes/{self.node}/time')
        return NodeTime(**data)

    def get_host(self):
        """获取节点的host信息"""
        data = self.client.http_request('GET', f'/nodes/{self.node}/hosts')
        return DigestData(**data)

    def get_netstat(self):
        """获取节点下所有虚机/容器的网络信息"""
        data = self.client.http_request('GET', f'/nodes/{self.node}/netstat')
        result = []
        for dev in data:
            dev['net_in'] = dev['in']
            dev['net_out'] = dev['out']
            result.append(NodeNetStats(**dev))
        return result

    def get_report(self) -> NodeReport:
        return NodeReport(
            type='NODE',
            name=self.node,
            status=self.status,
            uptime=int(self.uptime),
            cpu_total=int(self.maxcpu),
            cpu_used=round(self.maxcpu * self.cpu, 2),
            mem_total=int(self.maxmem),
            mem_used=int(self.mem),
            disk_total=int(self.maxdisk),
            disk_used=int(self.disk),
            vm_active_number=len(self.get_netstat())
        )
