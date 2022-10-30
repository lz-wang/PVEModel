"""https://pve.proxmox.com/pve-docs/api-viewer"""
import datetime
from typing import List

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import PveServerHttpResponseError
from .models.node import PVENode
from .models.pve import PVEInfo

urllib3.disable_warnings(InsecureRequestWarning)


class PVEClient(object):
    """Reference: https://pve.proxmox.com/wiki/Proxmox_VE_API"""

    def __init__(self, username: str, password: str, host: str,
                 port: int = 8006, realm: str = 'pam'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.realm = realm
        self.base_url = f'https://{self.host}:{self.port}/api2/json'
        self._refresh_cookies()

    def http_request(self, method: str, sub_url: str, data: dict = None,
                     auth: bool = True, verify: bool = False):
        url = f'{self.base_url}{sub_url}'
        if auth:
            resp = requests.request(method=method, url=url, data=data, cookies=self.cookie,
                                    headers=self.headers, verify=verify)

        else:
            resp = requests.request(method=method, url=url, data=data, verify=verify)

        if resp.status_code == 200:
            return resp.json()['data']
        else:
            raise PveServerHttpResponseError(f'code={resp.status_code}, text={resp.text}')

    def _refresh_cookies(self):
        data = dict(username=f'{self.username}@{self.realm}', password=self.password)
        resp_data = self.http_request('POST', '/access/ticket', data, auth=False)
        self.cookies_time = datetime.datetime.now()
        self.cookie = {'PVEAuthCookie': resp_data['ticket']}
        self.csrf_prevention_token = resp_data['CSRFPreventionToken']
        self.headers = {
            'PVEAuthCookie': resp_data['ticket'],
            'CSRFPreventionToken': self.csrf_prevention_token
        }

    def get_info(self) -> PVEInfo:
        """获取 PVE 集群的信息"""
        info = self.http_request('GET', '/version')
        return PVEInfo(**info)

    def get_nodes(self) -> List[PVENode]:
        """获取 PVE 集群的节点信息"""
        nodes = self.http_request('GET', '/nodes')
        nodes = [{**n, **{'client': self}} for n in nodes]
        return [PVENode(**node) for node in nodes]
