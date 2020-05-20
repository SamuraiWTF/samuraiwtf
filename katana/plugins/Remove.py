from plugins import Plugin
import os
import os.path
import shutil


class Remove(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["rm"]

    @staticmethod
    def _remove(path):
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True
        else:
            return False

    def any(self, params):
        self._validate_params(params, ['path'], 'rm')
        if isinstance(params.get("path"), str):
            result = self._remove(params.get("path"))
        else:
            result = False
            for path in params.get("path"):
                result = result or self._remove(path)

        if result:
            return True, None
        else:
            return False, "Nothing to remove. Path does not exist: {}".format(params.get("path"))
