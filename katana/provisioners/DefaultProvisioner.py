from provisioners import BaseProvisioner
import katanaerrors


class DefaultProvisioner(BaseProvisioner.BaseProvisioner):
    def __init__(self, module_info):
        super(DefaultProvisioner, self).__init__(module_info)

    def install(self):
        self._run_function("install")

    def remove(self):
        self._run_function("remove")

    def start(self):
        self._run_function("start")

    def stop(self):
        self._run_function("stop")

    def _run_function(self, func_name):
        func = self.module_info.get(func_name, {})
        if func is None:
            raise katanaerrors.NotImplemented(func_name, "DefaultProvisioner", self.get_name())
        elif len(func) == 0:
            print("There are no tasks defined in '{}.{}'".format(self.get_name(), func_name))
        else:
            print("Running '{}' tasks for module '{}'...".format(func_name, self.get_name()))
            for task in func:
                self._run_task(task, func_name)

    def _run_task(self, task, func):
        task_type = None

        for key in task:
            if key.lower() == "name":
                print("Task Name: {}".format(task.get(key)))
            else:
                task_type = key
                print("---> Running: {} {}".format(task_type, func))
                break

        plugin = BaseProvisioner.BaseProvisioner.get_plugin(task_type)

        if hasattr(plugin, 'any') and not hasattr(plugin, func):
            func = 'any'

        if hasattr(plugin, func) and callable(getattr(plugin, func)):
            method_to_call = getattr(plugin, func)
            result, msg = method_to_call(task.get(task_type))
            if result:
                print("     + changed")
            else:
                print("     X no change")
            if msg is not None:
                print("       {}".format(msg))

        else:
            raise katanaerrors.MissingFunction(func, task_type)
