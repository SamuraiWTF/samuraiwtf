from plugins import Plugin

import subprocess
import shlex
import os.path
import os


class Command(Plugin):
    '''
    module: command
    options:
        cmd:
            type: str
            description:
                - the command to run
        shell:
            type: bool
            description:
                - When true the command is executed with a shell, allowing for shell expansions to work.
        unsafe:
            type: bool
            description:
                - When true the command string is passed straight into the subprocess call.
    '''
    @classmethod
    def get_aliases(cls):
        return ["command"]

    def any(self, params):
        self._validate_params(params, ['cmd'], 'command')

        command_list = params.get('cmd')
        shell = params.get('shell')
        if not params.get('unsafe'):
            command_list = shlex.split(command_list)
        results = subprocess.run(command_list, shell=shell, cwd=params.get('cwd')) 

        return True, None

        # start_status_code = subprocess.call(['systemctl', 'start', params.get('name')])