import json
import time

import pytest
from loguru import logger as log

from src.client import PVEClient
from src.models.node import PVENode
from src.models.vm import PVEVm
from src.utils import pretty_time_delta, pretty_file_size

pve: PVEClient


def setup():
    global pve
    with open('../secret_test.json', 'r') as f:
        cred = json.load(f)
    pve = PVEClient(**cred)


def test_get_status():
    pve_info = pve.get_info()
    log.info(pve_info)
    nodes = pve.get_nodes()
    for node in nodes:
        log.info(f'PVE node, name={node.node}, status={node.status}, '
                 f'uptime={pretty_time_delta(float(node.uptime))}, '
                 f'cpu_total={node.maxcpu}c, '
                 f'cpu_used={round(node.maxcpu * node.cpu, 2)}c '
                 f'mem_total={pretty_file_size(float(node.maxmem))}, '
                 f'mem_used={pretty_file_size(float(node.mem))}, '
                 f'disk_total={pretty_file_size(float(node.maxdisk))}, '
                 f'disk_used={pretty_file_size(float(node.disk))}')
        vms_net = node.get_netstat()
        for vm_net in vms_net:
            log.info(f'VM: ID={vm_net.vmid}, '
                     f'net_in={pretty_file_size(float(vm_net.net_in))},'
                     f'net_out={pretty_file_size(float(vm_net.net_out))}')

        log.info(node.get_report().json())
        vms = node.get_vms()
        for vm in vms:
            log.info(f'{vm.get_report().json()}')


def vm_action(pve_node: PVENode):
    pve_vms = pve_node.get_vms()
    for pve_vm in pve_vms:
        if pve_vm.vmid == 107:
            assert pve_vm.name == 'CentOS7'
            if pve_vm.is_running():
                pve_vm.vm_shutdown()
                t = time.time()
                while True:
                    if time.time() - t >= 60 and pve_vm.is_running():
                        pve_vm.vm_stop()
                        break
                    if pve_vm.is_stopped():
                        break

            if pve_vm.is_stopped():
                pve_vm.vm_start()

            # if pve_vm.is_running():
            #     pve_vm.vm_reboot()

            if pve_vm.is_running():
                pve_vm.vm_suspend()

            if pve_vm.is_paused():
                pve_vm.vm_resume()


def make_cpu_data(vm: PVEVm):
    for _ in range(60):
        vm_status = vm.get_status()
        print(f'"{round(vm_status.cpu, 4)}"', end=', ')
        time.sleep(1)


if __name__ == "__main__":
    pytest.main()
