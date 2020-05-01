import yaml
import os


def read_repo():
    if os.path.exists("installed.yml"):
        with open("installed.yml", 'r') as stream:
            return yaml.load(stream)
    else:
        return {}


def write_repo(data):
    with open("installed.yml", 'w') as stream:
        yaml.dump(data, stream)


def set_installed(name, version):
    data = read_repo()
    data[name] = version
    write_repo(data)


def set_removed(name):
    data = read_repo()
    del data[name]
    write_repo(data)
