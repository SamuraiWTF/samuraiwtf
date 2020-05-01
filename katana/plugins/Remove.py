from plugins import Plugin
import os
import os.path
import shutil


class Remove(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["rm"]

    def _all(self, params):
        self._validate_params(params, ['path'], 'rm')
        if os.path.exists(params.get("path")):
            if os.path.isfile(params.get("path")):
                os.remove(params.get("path"))
            elif os.path.isdir(params.get("path")):
                shutil.rmtree(params.get("path"))
            return True, None
        else:
            return False, "Nothing to remove. Path does not exist: {}".format(params.get("path"))

    def remove(self, params):
        return self._all(params)
