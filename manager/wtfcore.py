from os import listdir
from os.path import isdir, join, dirname
import yaml
import play_runner

module_dict = {}

def load_module_info(path):
  with open(path, 'r') as stream:
    module_info = yaml.load(stream)
    module_info['path'] = dirname(path)
    module_dict[module_info.get('name')] = module_info
    return module_info

def list_modules(path='../modules/', module_list=[]):
  if len(module_list) == 0:
    module_dict.clear()

  file_list = listdir(path)
  for f in file_list:
    file_path = join(path, f)
    if isdir(file_path):
      list_modules(file_path, module_list)
    elif f=='wtfmodule.yml':
      module_info = load_module_info(file_path)
      if module_info is not None:
        module_list.append(module_info)
  return module_list

def get_module_info(name):
  return module_dict.get(name)

def install_module(name):
  if len(module_dict) == 0:
    list_modules()
    print(module_dict)
  module_info = module_dict.get(name)
  print("found module info: {}".format(module_info))
  if 'playbook' in module_info.get('install', {}):
    playbook_path = join(module_info.get('path'), module_info.get('install', {}).get('playbook'))
    with open(playbook_path, 'r') as stream:
      playbook_tasks = yaml.load(stream)
      print("Running playbook at: {}".format(playbook_path))
      playbook_source = dict(name = name,
        hosts = 'all',
        connection = 'local',
        become = 'yes',
        tasks = playbook_tasks)
      print("Playbook source: {}".format(playbook_source))
      play_runner.run_play(playbook_source)
