from plugins import Plugin
import os.path
import requests
import re
from tarfile import TarFile
import tarfile

class Unarchive(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["unarchive"]

    def any(self, params):
        self._validate_params(params, ['url', 'dest'], 'unarchive')

        # if os.path.exists(params.get('dest')) and not params.get('overwrite', False):
        #     return False, 'The specified file already exists: {}'.format(params.get('dest'))
        # else:
        r = requests.get(params.get('url'), stream=True)

        cd = r.headers['content-disposition']
        if cd is not None and len(cd) > 0:
            temp_file_name = '/tmp/{}'.format(re.findall("filename=(.+)", cd)[0])
        else:
            temp_file_name = '/tmp/tempdownload.tar.gz'

        if not os.path.exists(temp_file_name):
            with open(temp_file_name, "wb") as output:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        output.write(chunk)

            tar = tarfile.open(temp_file_name)
            tar.extractall(path=params.get('dest'))
            tar.close()
            return True, None
        else:
            return False, "The file '{}' already exists, so this task was skipped.".format(temp_file_name)
