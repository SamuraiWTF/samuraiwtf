from plugins import Plugin
import requests
import os
import os.path
import katanaerrors


class GetUrl(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["get_url"]

    def any(self, params):
        self._validate_params(params, ['url', 'dest'], 'get_url')

        if os.path.exists(params.get('dest')) and not params.get('overwrite', False):
            return False, 'The specified file already exists: {}'.format(params.get('dest'))
        else:
            r = requests.get(params.get('url'), stream=True)

            with open(params.get("dest"), "wb") as output:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        output.write(chunk)
            return True, None
