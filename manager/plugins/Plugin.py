import wtferrors

class Plugin(object):

  def _validate_params(self, params, required_params, plugin_name):
    for key in required_params:
      if key not in params.keys():
       raise wtferrors.MissingRequiredParam(key, plugin_name)



