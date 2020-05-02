from plugins import Plugin
import os.path
import os
import re
import fileinput
import katanaerrors


class Replace(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["replace"]

    def any(self, params):
        self._validate_params(params, ['path', 'regexp', 'replace'], 'replace')

        if not os.path.exists(params.get("path")):
            raise katanaerrors.CriticalFunctionFailure("replace", message="The specified file is missing: {}".format(params.get("path")))
        else:
            with fileinput.FileInput(params.get("path"), inplace=True) as file:
                for line in file:
                    print(re.sub(params.get('regexp'), params.get('replace'), line))
            return True, None
