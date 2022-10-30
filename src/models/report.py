from pydantic import BaseModel


class BaseReport(BaseModel):
    type: str
    name: str
    status: str
    uptime: int
    cpu_total: int
    cpu_used: float
    mem_total: int
    mem_used: int
    disk_total: int
    disk_used: int


class NodeReport(BaseReport):
    vm_active_number: int


class VMReport(BaseReport):
    vm_id: int
    qm_status: str
    disk_read: int
    disk_write: int
    net_in: int
    net_out: int
