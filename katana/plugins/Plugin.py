import katanaerrors


class Plugin(object):

    def _validate_params(self, params, required_params, plugin_name):
        for key in required_params:
            if params is None or key not in params.keys():
                raise katanaerrors.MissingRequiredParam(key, plugin_name)

    @classmethod
    def get_aliases(cls):
        return [cls.__name__]
