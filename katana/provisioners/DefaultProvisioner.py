from provisioners import BaseProvisioner
import katanacore
import katanaerrors


class DefaultProvisioner(BaseProvisioner.BaseProvisioner):
    def __init__(self, module_info):
        super(DefaultProvisioner, self).__init__(module_info)

    def install(self):
        for dependency in self.get_dependencies():
            if katanacore.status_module(dependency) == 'not installed':
                katanacore.install_module(dependency)
        self._run_function("install")

    def remove(self):
        self._run_function("remove")

    def start(self):
        for dependency in self.get_dependencies():
            if katanacore.status_module(dependency) != 'running':
                katanacore.start_module(dependency)
        self._run_function("start")

    def stop(self):
        self._run_function("stop")

    def _run_function(self, func_name):
        func = self.module_info.get(func_name)
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

    def status(self):
        """Determine the current status of the module tied to this provisioner.

        :return: str representing the module status as one of ['not installed', 'installed', 'running', 'stopped']
        """
        status_checks = self.module_info.get('status', {})

        print("checking status for {}".format(status_checks))

        try:
            has_run_check = False
            if 'running' in status_checks:
                has_run_check = True
                print("doing running check...")
                if self._do_checks(status_checks.get('running')) == 0:
                    return 'running'

            if 'installed' in status_checks:
                print("doing installed check...")
                if self._do_checks(status_checks.get('installed')) == 0:
                    if has_run_check:
                        return "stopped"
                    else:
                        return "installed"
                else:
                    return "not installed"
            else:
                return "unknown"
        except katanaerrors.BlockedByDependencyException:
            return "blocked"

    def _do_checks(self, checks):
        failed_checks = 0
        for check_type in checks.keys():
            check_pair = checks.get(check_type)
            print("Check pair: {}".format(check_pair))
            for check_key in check_pair.keys():
                check_value = check_pair.get(check_key)
                print("found check '{}' with value '{}'.".format(check_key, check_value))
                check_plugin = BaseProvisioner.BaseProvisioner.get_plugin(check_type)
                print("check plugin: {}".format(check_plugin))
                if check_plugin is None:
                    raise katanaerrors.NotImplemented(check_type, 'DefaultProvisioner', self.module_info.get('name'))
                elif hasattr(check_plugin, check_key) and callable(getattr(check_plugin, check_key)):
                    method_to_call = getattr(check_plugin, check_key)
                    if not method_to_call(check_value):
                        failed_checks = failed_checks + 1
                else:
                    raise katanaerrors.MissingFunction(check_type, check_key)
        return failed_checks