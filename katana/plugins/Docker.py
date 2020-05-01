from plugins import Plugin
import docker
import katanaerrors


class Docker(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["docker"]

    def install(self, params):
        self._validate_params(params, ['name', 'image'], 'docker')
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')

        container_list = client.containers.list(filters={'name': params.get('name')}, all=True)

        port_mappings = {}
        for container_port in params.get('ports').keys():
            port_mappings[container_port] = ('127.0.0.1', params.get('ports').get(container_port))

        if len(container_list) > 0:
            return False, "A container named '{}' is already installed.".format(params.get('name'))
        else:
            images = client.images.list(name=params.get('image'))
            if len(images) == 0:
                print("       Image not available locally. Pulling from DockerHub.")
                client.images.pull(params.get('image'))

            container = client.containers.create(image=params.get('image'), name=params.get('name'), detach=True,
                                                 ports=port_mappings)
            container.logs()
            return True, None

    def remove(self, params):
        self._validate_params(params, ['name'], 'docker')
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        container_list = client.containers.list(filters={'name': params.get('name')}, all=True)

        if len(container_list) == 0:
            return False, "No container named '{}' was found. It will need to be installed before you can remove it.".format(
                params.get('name'))
        elif container_list[0].status == "running":
            raise katanaerrors.CriticalFunctionFailure('docker', 'Cannot remove a running container.')
        else:
            container_list[0].remove(v=True)
            return True, "Container removed: '{}".format(params.get('name'))

    def start(self, params):
        self._validate_params(params, ['name'], 'docker')
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        container_list = client.containers.list(filters={'name': params.get('name')}, all=True)

        if len(container_list) == 0:
            return False, "No container named '{}' was found. It will need to be installed before you can start it.".format(
                params.get('name'))
        elif container_list[0].status == "running":
            return False, "The '{}' container is already running.".format(params.get('name'))
        else:
            container_list[0].start()
            return True, None

    def stop(self, params):
        self._validate_params(params, ['name'], 'docker')
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        container_list = client.containers.list(filters={'name': params.get('name')}, all=True)

        if len(container_list) == 0:
            return False, "No container named '{}' was found. It will need to be installed before you can stop it.".format(
                params.get('name'))
        elif container_list[0].status != "running":
            return False, "The '{}' container is not running.".format(params.get('name'))
        else:
            container_list[0].stop()
            return True, None
