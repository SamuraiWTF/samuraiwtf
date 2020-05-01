from plugins import Plugin
from git import Repo
import os.path


class Git(Plugin):

    @classmethod
    def get_aliases(cls):
        return ["git"]

    def install(self, params):
        self._validate_params(params, ['repo', 'dest'], 'git')
        if os.path.exists(params.get("dest")):
            return (
                False,
                "Git could not clone because the specified dest path already exists: {}".format(params.get("dest")))
        else:
            repo = Repo.clone_from(url=params.get("repo"), to_path=params.get("dest"), depth=1)
            repo.close()
            return True, None
