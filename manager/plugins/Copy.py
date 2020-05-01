from plugins import Plugin
import os.path
import os


class Copy(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["copy"]

    def any(self, params):
        self._validate_params(params, ['dest', 'content'], 'copy')
        if not params.get("force", False) and os.path.exists(params.get("dest")):
            return False, "The specified destination path exists: {}".format(params.get("dest"))
        else:
            with open(params.get("dest"), 'w') as out_file:
                out_file.write(params.get('content'))
                if "mode" in params:
                    os.chmod(params.get("dest"), params.get("mode"))

            return True, None

