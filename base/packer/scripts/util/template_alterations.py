#!/usr/bin/env python3
from time import sleep
import json
from pprint import pprint
from inspect import getframeinfo, currentframe
from copy import deepcopy

## global variables
scripts_path = './scripts'
build_script = scripts_path + '/build'
ansible_scripts = scripts_path + '/'
bento_path = build_script + '/bento'
# bento_debian_path = bento_path + '/packer_templates/debian'
bento_ubuntu_path = bento_path + '/packer_templates/ubuntu'
base_box_name = 'samuraiwtf-base_box'

# start each section with a pre-defined message and it's name
def section_intro(current_func):
    # adding extra spacing
    print('')

    # using logging function to print
    logging('Starting {} section'.format(current_func))

    # adding extra spacing
    print('')

def section_outro(current_func):
    # adding extra spacing
    print('')

    # using logging function to print
    logging('Exiting {} section'.format(current_func))

    # adding extra spacing
    print('')

# logging func
def logging(log_str):
    pprint(log_str)

# def del_from_list(list_obj, list_del):
#     for objz in li

# alterations to the environment variables section of the packer template
def var_alterations(json_obj):

    # starting section by logging name
    section_intro(getframeinfo(currentframe()).function)

    # only selecting the vars section from the template
    variables_dict = json_obj['variables']

    # list of items to remove from the template
    remove_list = [ 'version', 'http_proxy', 'https_proxy', 'no_proxy',
        'mirror', 'mirror_directory', 'iso_name', 'build_timestamp',
        'git_revision', 'guest_additions_url' ]

    # removing all items in list above
    for var in remove_list:
        logging('removed: {}'.format(var))
        del variables_dict[var]

    # either adding or updating values in template
    sub_dict = {
        'headless': '',
        'iso_checksum': '',
        'iso_checksum_type': '',
        'build_directory': '.',
        # 'bento_debian_dir': bento_debian_path,
        'bento_ubuntu_dir': bento_ubuntu_path,
        'build_script_dir': build_script,
        'box_basename': base_box_name,
        # 'http_directory': bento_debian_path + '/http',
        'http_directory': bento_ubuntu_path + '/http',
        'memory': '4096'
    }

    # making alteration as defined above
    variables_dict.update(sub_dict)

    section_outro(getframeinfo(currentframe()).function)
    # returning altered object
    return json_obj

# alterations to the builders section of the packer template
def builders_alterations(json_obj):

    # starting section by logging name
    section_intro(getframeinfo(currentframe()).function)

    # only selecting the vars section from the template
    builders_list = json_obj['builders']

    # currently supported builders
    allowed_builders_list = [ 'virtualbox-iso', 'vmware-iso']
    # delcaring empty list (used later)
    removal_builders_list = [ ]

    # adding unsupported builders to be removed later
    for builder in builders_list:
        if builder['type'] not in allowed_builders_list:
            removal_builders_list.append(builder)

    # removing unsupported builders
    for removed in removal_builders_list:
        logging('removed: {}'.format(removed['type']))
        builders_list.remove(removed)

    # defining what properties have to be removed
    prop_removal = [ 'guest_additions_url' ]

    # defining what properties have to be updated/added
    prop_update = {
        'iso_url': '{{user `iso_url`}}'
    }

    # removing properties and logging
    for prop_rm in prop_removal:
        for builder_dict in builders_list:
            if prop_rm in builder_dict:
                logging('removed: {} from: {}'.format(prop_rm, builder_dict['type']))
                del builder_dict[prop_rm]

    # updating properties to desired state
    for builder_dict in builders_list:
        logging('updated property: {} in: {}'.format(prop_update, builder_dict['type']))
        builder_dict.update(prop_update)

    section_outro(getframeinfo(currentframe()).function)
    # returning altered object
    return json_obj

def prov_alterations(json_obj):

    # starting section by logging name
    section_intro(getframeinfo(currentframe()).function)

    prov_list = json_obj['provisioners']

    bento_prov = prov_list[0]

    ## altering the only bash provisioner bento has by default
    # making list of how many vars (in reverse order) we want to remove
    env_var_list = [ 'no_proxy', 'https_proxy', 'http_proxy' ]

    # removing env vars
    for env in env_var_list:
        logging('removing: {}'.format(env))
        bento_prov['environment_vars'].pop()

    # creating deepcopy of env to use later, so we can alter it and it not
    #   mess up the original:
    #   https://stackoverflow.com/questions/2612802/how-to-clone-or-copy-a-list
    bento_copy_prov = deepcopy(bento_prov)

    # creating list to save last 2 scripts from bento, so they can be run
    #   later after all other provisioing (they are used for cleanup)
    cleanup_scripts = []

    # minimize.sh
    cleanup_scripts.append(bento_prov['scripts'].pop())

    # cleanup.sh
    cleanup_scripts.append(bento_prov['scripts'].pop())

    # bleachbit.sh
    # cleanup_scripts.append(
    #     '{{user `build_script_dir`}}/bleachbit.sh'
    # )

    # adding my new scripts to the scripts section
    # all my custom scripts (desktop & ansible) are in build_script_dir
    my_scripts_list = [
        '{{user `build_script_dir`}}/upgrade.sh',
        '{{user `build_script_dir`}}/desktop-env.sh',
        '{{user `build_script_dir`}}/ansible.sh'
    ]

    # adding my personal scripts
    for my_script in my_scripts_list:
        bento_prov['scripts'].append(my_script)

    ### Prepending to prov_list
    ## shell-local: compressing the config dir to upload later
    prov_list.insert(0,
        {
            "type": "shell-local",
            "execute_command": [ "bash", "-c", "{{.Script}}" ],
            "command": "pushd ./scripts/build/ || exit 1 && tar -czvf config.tgz config && popd"

        }
    )
    ### need to add the following provisions
    ## FILE: upload compressed config files to /tmp
    prov_list.append(
        {
            'type': 'file',
            'source': build_script + '/config.tgz',
            'destination': '/tmp/config.tgz'
        }
    )

    ## ANSIBLE: run all the samurai scripts
    prov_list.append(
        {
            'type': 'ansible-local',
            'playbook_dir': build_script + '/install',
            'playbook_file': './scripts/build/install/samuraiwtf.yml'
        }
    )

    ## SHELL: move last 2 scripts (cleanup) to bottom
    # clearing scripts section of all previous scripts
    bento_copy_prov['scripts'].clear()

    for scriptz in reversed(cleanup_scripts):
        bento_copy_prov['scripts'].append(scriptz)

    # altering the the path for the cleanup.sh, so it
    # doesn't try to uninstall X11 packages
    bento_copy_prov['scripts'][0] = "{{user `build_script_dir`}}/cleanup.sh"

    # appending to provisioners list
    prov_list.append(bento_copy_prov)

    section_outro(getframeinfo(currentframe()).function)
    return json_obj

def post_processor_alteration(json_obj):
    section_intro(getframeinfo(currentframe()).function)

    # getting current post-processors
    post_processors = json_obj['post-processors']

    # updating vagrant processor
    post_processors[0].update(
        {
            'compression_level': 9
        }
    )

    # defining new post processors
    vagrant_cloud_dict = {
        'type': 'vagrant-cloud',
        'box_tag': '{{user `vagrant_box_name`}}',
        'access_token': '{{user `vagrant_cloud_token`}}',
        'version': '{{user `vm_version`}}'
    }

    # group 1 of post processors, need to group because of this:
    # https://packer.io/docs/post-processors/vagrant-cloud.html#use-with-the-artifice-post-processor
    post_processors_group1 = [
        post_processors[0],
        vagrant_cloud_dict
    ]

    # clean out old bento vagrant post-provisioner
    post_processors.clear()

    # updating to make first grouping to process for post-processors
    post_processors.insert(0, post_processors_group1)

    section_outro(getframeinfo(currentframe()).function)
    return json_obj

if __name__ == "__main__":
    # location of old debian template
    # old_packer_file = bento_debian_path + '/debian-10.2-amd64.json'
    old_packer_file = bento_ubuntu_path + '/ubuntu-20.04-amd64.json'
    # location of file getting outputted
    new_packer_file = 'samurai.json'

    # read in old file
    with open(old_packer_file, 'r') as current_template:
        data = current_template.read()

    # replacing all instances of template dir with a user var
    #   of bento_debian_path, because that is the location it
    #   is expecting for relative file traversal
    # data = data.replace('template_dir', 'user `bento_debian_dir`')
    data = data.replace('template_dir', 'user `bento_ubuntu_dir`')

    # converting to json object
    obj = json.loads(data)

    # altering variable section of packer json template
    updated_obj = var_alterations(obj)

    # altering builders section of packer json template
    updated_obj = builders_alterations(updated_obj)

    # altering provisioners section of packer json template
    updated_obj = prov_alterations(updated_obj)

    # adding to post-processors
    updated_obj = post_processor_alteration(updated_obj)

    # logging final object
    # logging(updated_obj)

    # writing out to file
    with open('samurai.json', 'w', encoding='utf-8') as f:
        json.dump(updated_obj, f, ensure_ascii=False, indent=4)
