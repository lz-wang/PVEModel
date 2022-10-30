from typing import Optional, Any, Dict

from pydantic import BaseModel

from .report import VMReport


class VMBlock(BaseModel):
    failed_rd_operations: int
    failed_wr_operations: int
    flush_total_time_ns: int
    wr_highest_offset: int
    failed_flush_operations: int
    invalid_flush_operations: int
    wr_merged: int
    account_invalid: bool
    unmap_merged: int
    account_failed: int
    unmap_operations: int
    rd_merged: int
    idle_time_ns: Optional[int]
    failed_unmap_operations: int
    wr_total_time_ns: int
    rd_bytes: int
    unmap_bytes: int
    timed_stats: list
    invalid_wr_operations: int
    rd_total_time_ns: int
    wr_bytes: int
    invalid_unmap_operations: int
    flush_operations: int
    invalid_rd_operations: int
    unmap_total_time_ns: int
    rd_operations: int
    wr_operations: int


class ProxmoxSupport(BaseModel):
    pass


class VMStatus(BaseModel):
    vmid: int
    status: str
    qmpstatus: str
    uptime: int
    cpus: int
    cpu: float
    maxmem: int
    mem: int
    maxdisk: int
    disk: int
    diskread: int
    diskwrite: int
    netin: int
    netout: int
    pid: Optional[int]
    ha: dict
    running_machine: str = ''  # need update by raw dict
    running_qemu: str = ''  # need update by raw dict
    proxmox_support: dict = ''  # need update by raw dict
    ballooninfo: Optional[dict]
    nics: Optional[dict]
    blockstat: Optional[Dict[str, VMBlock]]


class PVEVm(BaseModel):
    vmid: int
    name: str
    status: str
    uptime: int
    cpus: int
    cpu: int
    mem: int
    maxmem: int
    netin: int
    netout: int
    disk: int
    diskread: int
    diskwrite: int
    maxdisk: int
    pid: Optional[int]
    balloon_min: Optional[int]
    shares: Optional[int]
    client: Optional[Any]
    node: Optional[Any]

    def get_status(self):
        sub_url = f'/nodes/{self.node.node}/qemu/{self.vmid}/status/current'
        data = self.client.http_request('GET', sub_url)
        vm_status = VMStatus(**data)
        vm_status.running_machine = data.get('running-machine', '')
        vm_status.running_qemu = data.get('running-qemu', '')
        vm_status.proxmox_support = data.get('proxmox-support')

        return vm_status

    def is_started(self):
        return self.get_status().status == "running"

    def is_stopped(self):
        return self.get_status().status == "stopped"

    def is_running(self):
        return self.get_status().status == "running" and self.get_status().qmpstatus == "running"

    def is_paused(self):
        return self.get_status().qmpstatus == "paused"

    def _change_status(self, status: str):
        cur_status = self.get_status().status
        # log.warning(f'[VM_id={self.vmid}][{self.name}] changing status: {cur_status} -> {status}')
        sub_url = f'/nodes/{self.node.node}/qemu/{self.vmid}/status/{status}'
        resp = self.client.http_request('POST', sub_url)
        # log.success(f'[VM_id={self.vmid}][{self.name}] change status OK, resp={resp}')
        return resp

    def vm_reboot(self):
        return self._change_status('reboot')

    def vm_start(self):
        return self._change_status('start')

    def vm_stop(self):
        return self._change_status('stop')

    def vm_shutdown(self):
        return self._change_status('shutdown')

    def vm_suspend(self):
        return self._change_status('suspend')

    def vm_resume(self):
        return self._change_status('resume')

    def get_report(self) -> VMReport:
        vm = self.get_status()
        return VMReport(
            type='VM',
            vm_id=vm.vmid,
            qm_status=vm.qmpstatus,
            name=self.name,
            status=vm.status,
            uptime=int(vm.uptime),
            cpu_total=int(vm.cpus),
            cpu_used=round(vm.cpus * vm.cpu, 2),
            mem_total=int(vm.maxmem),
            mem_used=int(vm.mem),
            disk_total=int(vm.maxdisk),
            disk_used=int(vm.disk),
            disk_read=int(vm.diskread),
            disk_write=int(vm.diskwrite),
            net_in=int(vm.netin),
            net_out=int(vm.netout)
        )
