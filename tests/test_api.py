import json
import time

from loguru import logger as log

from src.client import PVEClient
from src.models.node import PVENode
from src.models.vm import PVEVm


def show_status(pve_vm_, timeout=10):
    t0 = time.time()
    while time.time() - t0 < timeout:
        cur_status = pve_vm_.get_status()
        log.info(f"[{pve_vm_.name}] vm -> {cur_status.status}, qemu -> {cur_status.qmpstatus}")
        time.sleep(5)


def test_vm(pve_node: PVENode):
    pve_vms = pve_node.get_vms()
    for pve_vm in pve_vms:
        if pve_vm.vmid == 107:
            assert pve_vm.name == 'CentOS7'
            show_status(pve_vm, 1)
            if pve_vm.is_running():
                pve_vm.vm_shutdown()
                t = time.time()
                while True:
                    if time.time() - t >= 60 and pve_vm.is_running():
                        pve_vm.vm_stop()
                        break
                    if pve_vm.is_stopped():
                        break
                    show_status(pve_vm)

            if pve_vm.is_stopped():
                pve_vm.vm_start()
                show_status(pve_vm)

            # if pve_vm.is_running():
            #     pve_vm.vm_reboot()
            #     show_status(pve_vm, 30)

            if pve_vm.is_running():
                pve_vm.vm_suspend()
                show_status(pve_vm)

            if pve_vm.is_paused():
                pve_vm.vm_resume()
                show_status(pve_vm)


def make_cpu_data(vm: PVEVm):
    for _ in range(60):
        vm_status = vm.get_status()
        print(f'"{round(vm_status.cpu, 4)}"', end=', ')
        time.sleep(1)


if __name__ == "__main__":
    with open('../secret.json', 'r') as f:
        cred = json.load(f)
    pve = PVEClient(**cred)

    # show info
    pve_info = pve.get_info()
    log.info(f'PVE: release={pve_info.release}, version={pve_info.version}')

    # show nodes
    pve_nodes = pve.get_nodes()

    # show vms
    for pn in pve_nodes:
        disks = pn.get_disks()
        status = pn.get_status()
        node_time = pn.get_time()
        host = pn.get_host()
        netstat = pn.get_netstat()
        # test_vm(pn)
        for pvm in pn.get_vms():
            if pvm.vmid == 108:
                make_cpu_data(pvm)
