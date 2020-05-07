#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

sudo amazon-linux-extras install ansible2

pushd "$DIR"/../.. || exit

sudo ansible-playbook -K base/amazon-linux/local_playbook.yml

if [[ "$1" == "--develop" ]]; then
  sudo ln -s "$(pwd)/katana/" /opt/katana
else
  sudo mkdir -p /opt/katana
  sudo cp -R katana/* /opt/katana/
fi

popd