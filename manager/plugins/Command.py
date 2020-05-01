from plugins import Plugin

import subprocess
import shlex
import os.path
import os


class Command(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["command"]

    def any(self, params):
        self._validate_params(params, ['cmd'], 'command')

        command_list = shlex.split(params.get('cmd'))
        results = subprocess.run(command_list, cwd=params.get('cwd'))

        return True, None

        # start_status_code = subprocess.call(['systemctl', 'start', params.get('name')])