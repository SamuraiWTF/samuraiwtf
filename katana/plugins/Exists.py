from plugins import Plugin
import os.path
import subprocess
import docker


class Exists(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["exists"]

    def path(self, value):
        return os.path.exists(value)

    def service(self, value):
        return_code = subprocess.call(['systemctl', 'status', value])
        return return_code != 4

    def docker(self, value):
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        container_list = client.containers.list(filters={'name': value}, all=True)

        return len(container_list) > 0
