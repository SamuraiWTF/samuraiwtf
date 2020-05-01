from plugins import Plugin
import os.path
import os
import katanaerrors


class LineInFile(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["lineinfile"]

    def any(self, params):
        self._validate_params(params, ['dest', 'line'], 'lineinfile')
        state = params.get('state', 'present')
        if state not in ['present', 'absent']:
            raise katanaerrors.UnrecognizedParamValue('state', state, 'lineinfile', 'present, absent')

        lines = []
        if os.path.exists(params.get("dest")):
            with open(params.get('dest'), 'r') as f:
                lines = f.readlines()

        line = "{}\n".format(params.get('line'))

        if line in lines:
            if state == 'present':
                return False, "Line is already present."
            else:
                lines.remove(line)
                with open(params.get('dest'), 'w') as f:
                    f.writelines(lines)
                return True, None
        else:
            if state == "present":
                lines.append(line)
                with open(params.get('dest'), 'w') as f:
                    f.writelines(lines)
                return True, None
            else:
                return False, "Line is already not present."
