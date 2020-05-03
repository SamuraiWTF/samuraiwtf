from os import listdir
from os.path import abspath, realpath, join, dirname, isfile

from plugins import Plugin


class BaseProvisioner(object):

    plugins = {}

    def __init__(self, module_info):
        self.module_info = module_info
        self._load_plugins()

    def get_name(self):
        return self.module_info.get("name", "(unknown)")

    def get_description(self):
        return self.module_info.get("description", "(Not specified)")

    def get_category(self):
        return self.module_info.get("category", "(none)")

    def get_href(self):
        return self.module_info.get("href", None)

    @classmethod
    def _load_plugins(cls):
        if len(BaseProvisioner.plugins) == 0:
            my_path = abspath(dirname(__file__))
            path = realpath(join(my_path, "../plugins"))

            file_list = listdir(path)
            for f in file_list:
                if not f.startswith('_'):
                    class_name = f[:-3]
                    mod = __import__("plugins." + class_name, fromlist=[class_name])
                    klass = getattr(mod, class_name)

                    plugin = klass()
                    if issubclass(klass, Plugin) and klass is not Plugin:
                        for alias in plugin.get_aliases():
                            # print("alias {} points to class:{}".format(alias, klass))
                            BaseProvisioner.plugins[alias] = plugin

    @classmethod
    def get_plugin(cls, alias):
        return BaseProvisioner.plugins.get(alias)
