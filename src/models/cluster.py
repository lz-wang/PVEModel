from typing import Any, Optional, List

from pydantic import BaseModel

from .node import PVENode
from .vm import PVEVM


class ClusterNodes(BaseModel):
    type: str
    level: str
    name: str
    ip: str
    id: str
    nodeid: int
    online: bool
    local: bool


class ClusterStatus(BaseModel):
    nodes: List[ClusterNodes]


class ClusterTask(BaseModel):
    type: str
    status: str
    user: str
    node: str
    id: str
    starttime: int
    endtime: int
    upid: str


class ClusterLog(BaseModel):
    user: str
    node: str
    time: int
    id: str
    uid: str
    pid: int
    pri: int
    tag: str
    msg: str


class ClusterResourcePool(BaseModel):
    pass


class ClusterResourceNode(PVENode):
    pass


class ClusterResourceQemu(PVEVM):
    pass


class ClusterResourceLxc(BaseModel):
    pass


class ClusterResourceOpenvz(BaseModel):
    pass


class ClusterResourceSdn(BaseModel):
    pass


class ClusterResourceStorage(BaseModel):
    type: str
    id: str
    status: str
    node: str
    maxdisk: int
    disk: int
    shared: bool
    content: str
    storage: str
    plugintype: str


class PVECluster(ClusterStatus):
    client: Optional[Any]

    def get_status(self) -> ClusterStatus:
        status = self.client.get_cluster().dict()
        return ClusterStatus(**status)

    def get_tasks(self) -> List[ClusterTask]:
        data = self.client.http_request('GET', '/cluster/tasks')
        tasks = [ClusterTask(**d) for d in data]
        return sorted(tasks, key=lambda task: task.endtime, reverse=True)

    def get_resource(self, resource_type: str = None):
        params = {'type': resource_type} if resource_type else None
        data = self.client.http_request('GET', '/cluster/resources', params=params)
        result = list()
        for d in data:
            match d['type']:
                case 'node':
                    result.append(ClusterResourceNode(**d))
                case 'qemu':
                    d['cpus'] = d['maxcpu']
                    result.append(ClusterResourceQemu(**d))
                case 'storage':
                    result.append(ClusterResourceStorage(**d))
                case _:
                    raise TypeError(f'Unknown data type: {d["type"]}')

        return result

    def get_log(self, number: int = 10) -> List[ClusterLog]:
        data = self.client.http_request('GET', '/cluster/log', params={'max': number})
        logs = [ClusterLog(**d) for d in data]
        return sorted(logs, key=lambda log: log.time, reverse=True)
