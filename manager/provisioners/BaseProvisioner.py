class BaseProvisioner(object):

  def __init__(self, module_info):
    self.module_info = module_info    

  def get_name(self):
    return self.module_info.get("name", "(unknown)")

  def get_description(self):
    return self.module_info.get("description", "(Not specified)")

