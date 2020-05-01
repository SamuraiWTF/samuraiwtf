from plugins import Command

import subprocess
import os.path
import os


class Yarn(Command):

    @classmethod
    def get_aliases(cls):
        return ["yarn"]

    def any(self, params):
        self._validate_params(params, ['path'], 'yarn')
        return super(Yarn, self).any({'cmd': 'yarn', 'cwd': params.get('path')})
