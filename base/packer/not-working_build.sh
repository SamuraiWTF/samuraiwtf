#!/usr/bin/env bash

set -${-//[s]/}eu${DEBUG+xv}o pipefail

if [[ ! -f variables.json ]] ; then

  # shellcheck disable=SC1091
  source scripts/setup/env_vars
  
  vagrant destroy -f
  vagrant box update
  vagrant up
  
  set +e
  vagrant ssh
  set -e

  unset VAGRANT_CLOUD_TOKEN  PACKET_API_KEY TEXTBELT_KEY

fi


# disabling firewall for vmware-iso build
# sudo ufw disable

if ! grep headless variables.json 1>/dev/null ; then
  # adding headless to json file
  vim variables.json
fi

# generating samurai.json packer template
scripts/util/template_alterations.py

# folders to compress
folder_array=(
  './scripts/build/:config'
  '../../:katana'
)

for array_item in "${folder_array[@]}" ; do
  path_to_folder="${array_item%:*}"
  folder_to_compress="${array_item##*:}"
  # compressing folder
  pushd "${path_to_folder}" || exit 1 && tar -czvf "${folder_to_compress}.tgz" "${folder_to_compress}" && popd

done

# building vagrant box
packer validate -only=virtualbox-iso -var-file variables.json samurai.json |& tee build.log

# building vagrant box
time packer build -only=virtualbox-iso -var-file variables.json samurai.json |& tee -a build.log
