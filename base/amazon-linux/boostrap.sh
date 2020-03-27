#!/bin/bash

sudo amazon-linux-extras install ansible2

pushd ~

# git clone --depth=1 --single-branch --branch amazon-linux https://github.com/SamuraiWTF/samuraiwtf.git
cd samuraiwtf

ansible-playbook -K base/amazon-linux/local_playbook.yml

popd