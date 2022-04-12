#!/usr/bin/env bash

set -e
env_file='/etc/profile.d/circleci.sh'

## Project setup functions
circle_ci(){
  project_url='https://github.com/elreydetoda/samuraiwtf-base_box.git'

  echo "export CIRCLECI=true" | sudo tee -a ${env_file} 1>/dev/null

  if [[ -d /vagrant ]] ; then
    ln -sf /vagrant/ ${HOME}/project
  else
    git clone ${project_url} ${HOME}/project
  fi
  echo "cd ${HOME}/project" >> ${HOME}/.bashrc

  . ${env_file}
  variables_gen

  if [[ ! -f ${HOME}/project/variables.json  ]] ; then
    cp ${HOME}/project/variables.json /vagrant
  fi
  get_secret
}

variables_gen(){
  # path_to_new_debian_shell_script='/vagrant/scripts/setup/debian.sh'
  path_to_new_ubuntu_shell_script='/vagrant/scripts/setup/ubuntu.sh'
  if [[ $CIRCLECI ]] ; then
    project_dir="${HOME}/project"
  else
    project_dir='/vagrant'
    . ${env_file}
    export CIRCLECI=''
  fi
  # installing deps
  echo 'Installing dependencies...'
  sudo apt-get install -y jq screen dirmngr

  pushd ${project_dir}
  # chmod +x ${path_to_new_debian_shell_script}
  chmod +x ${path_to_new_ubuntu_shell_script}
  # ${path_to_new_debian_shell_script}
  ${path_to_new_ubuntu_shell_script}
}

## base framework
selection_setup(){
  PROJECT=''
  # projects_array=( "variables_gen" "circle_ci")
  projects_array=( "variables_gen" )
  project_index=0
}

selection(){
  for project in "${projects_array[@]}"; do
    printf "%d) %s\n" $project_index $project
    project_index=$(( $project_index + 1 ))
  done

  printf 'Please choose a project: '
  read -r project_num

  if [ $project_num -ge 0 ] && [ $project_num -lt $project_index ] ; then
    ${projects_array[$project_num]}
  else
    echo 'no project selected'
    echo 'to set this up again'
    echo 'please run: vagrant provision'
    cleanup
    exit 1
  fi
}

get_secret(){

  private_key_location="${HOME}/.ssh/id_rsa"

  echo
  echo "What is the private key that you will be using to ssh into the server with? CTRL-d when done."
  private_key_var=$(cat)
  echo "${private_key_var}" > ${private_key_location}
  chmod 600 ${private_key_location}

}

cleanup(){
  sed -i 's,/vagrant/prov_vagrant/prov.sh,,' ~vagrant/.bashrc
  echo
  echo 'Forcing logout to reload environmental variables'
  echo
  ps -aux | grep vagrant | grep 'pts/0' | grep "[s]sh" | awk '{print $2}' | xargs kill
  # if [[ ! -z $project_num ]] ; then
  #   echo 'Powering off machine so you have proper dev env, please do a vagrant up'
  #   sudo shutdown -h now
  # fi
}
check_done(){
  echo
  echo 'Will that be all? (Y/n)'
  read -r donez_ans
  donez_ans=$(echo $donez_ans | tr '[:upper:]' '[:lower:]')
  if [[ !($donez_ans == 'n') ]] ; then
    donez=false
    cleanup
  fi
}
donez=true
while $donez ; do
  export CIRCLECI=''
  sudo apt-get update
  sudo apt-get install -y git tmux screen
  # for spacing
  echo
  selection_setup
  selection
  check_done
done
