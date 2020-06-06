from os import listdir, path
from os.path import isdir, join, dirname, realpath, abspath
import yaml
import katanaerrors
import re

module_dict = {}
locked_modules = []
lock_file_read = False


def load_module_info(path):
    with open(path, 'r') as stream:
        module_info = yaml.load(stream, Loader=yaml.SafeLoader)
        module_info['path'] = dirname(path)

        if re.fullmatch('[a-zA-Z][a-zA-Z0-9\-_]+', module_info['name']):
            provisioner_class = module_info.get("class", "provisioners.DefaultProvisioner")
            if "." in provisioner_class:
                class_name = provisioner_class[provisioner_class.rindex(".") + 1:]
            else:
                class_name = provisioner_class

            mod = __import__(provisioner_class, fromlist=[class_name])
            klass = getattr(mod, class_name)

            provisioner = klass(module_info)
            module_dict[module_info.get('name').lower()] = provisioner

            return provisioner
        else:
            print(f"ERROR: Module name is invalid. It must be a valid css id: {module_info['name']}")


def list_modules(path=None, module_list=None):
    if module_list is None:
        module_list = []
    if path is None:
        my_path = abspath(dirname(__file__))
        path = realpath(join(my_path, "modules"))

    if len(module_list) == 0:
        module_dict.clear()

    file_list = listdir(path)
    for f in file_list:
        file_path = join(path, f)
        if isdir(file_path):
            list_modules(file_path, module_list)
        elif f.endswith(".yml"):
            module_info = load_module_info(file_path)
            if module_info is not None:
                module_list.append(module_info)
    return module_list


def get_module_info(name):
    return module_dict.get(name)


def _run_function(module_name, function_name):
    if len(module_dict) == 0:
        list_modules()

    provisioner = module_dict.get(module_name.lower())
    if provisioner is None:
        raise katanaerrors.ModuleNotFound(module_name)

    if hasattr(provisioner, function_name) and callable(getattr(provisioner, function_name)):
        function_to_call = getattr(provisioner, function_name)
        return function_to_call()
    else:
        raise katanaerrors.NotImplemented(function_name, type(provisioner).__name__)


def install_module(name):
    _run_function(name, "install")


def remove_module(name):
    _run_function(name, "remove")


def start_module(name):
    _run_function(name, "start")


def stop_module(name):
    _run_function(name, "stop")


def status_module(name):
    return _run_function(name, "status")


def get_available_actions(module_name):
    provisioner = module_dict.get(module_name.lower())
    if provisioner is None:
        raise katanaerrors.ModuleNotFound(module_name)

    return provisioner.has_actions(module_name in load_locked_modules())


def lock_modules():
    global lock_file_read
    locked_modules.clear()

    if len(module_dict) == 0:
        list_modules()

    for module_name in module_dict.keys():
        status = status_module(module_name)
        if status in ['running', 'installed', 'stopped']:
            locked_modules.append(module_name)

    my_path = abspath(dirname(__file__))
    lock_file = join(my_path, "katana.lock")

    with open(lock_file, 'w') as lf:
        lf.write("\n".join(locked_modules))
    lock_file_read = False


def load_locked_modules():
    global lock_file_read
    if lock_file_read:
        return locked_modules
    else:
        my_path = abspath(dirname(__file__))
        lock_file = join(my_path, "katana.lock")

        if path.exists(lock_file):
            locked_modules.clear()
            with open(lock_file, 'r') as lf:
                for module in lf.readlines():
                    locked_modules.append(module.strip())
        else:
            locked_modules.clear()
        lock_file_read = True
        return locked_modules


