#!/usr/bin/env bash

set -exu

sudo apt-get install -y bleachbit

## base section
# declare all base options that aren't all sub-options (i.e. apt.*),
# and have only have one sub-options for bleachbit (i.e. journald.clean)
bleach_bit_options_array=( 'apt.*' 'deepscan.*' 'journald.clean'  )
##

## multi sub-options section
# define all the system sub-options wanted to run (i.e. system.cache)
system_options=( 'cache' 'free_disk_space' 'recent_documents' 'rotated_logs' 'tmp' 'trash' )
##

# defining function to append all sub-options to base array
append_array(){

    # define the prefix to add to all sub-options (i.e. system)
    prefix="${1}"

    # define all sub-options to append to prefix (i.e. cache)
    array_to_append=("${@:2}")

    # iterate on all the sub-options
    for i in "${array_to_append[@]}" ; do

        # append to base array full options (i.e. system.cache)
        bleach_bit_options_array+=("${prefix}.${i}")

    done
}

# append all system options
append_array "system" "${system_options[@]}"

# define the bleachbit command as
sudo bleachbit -c "${bleach_bit_options_array[@]}"

sudo apt-get purge -y bleachbit
sudo apt-get autoremove --purge -y
