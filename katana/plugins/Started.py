from plugins import Plugin
import os.path
import docker
import subprocess


class Started(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["started"]

    def service(self, value):
        return subprocess.call(['systemctl', 'status', value]) == 0

    def docker(self, value):
        if not self.service("docker"):
            return False

        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        container_list = client.containers.list(filters={'name': value}, all=True)

        if len(container_list) == 0:
            return False
        else:
            return container_list[0].status == "running"
