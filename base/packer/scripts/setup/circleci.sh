## CI info
# packet info
if [[ -z "${PACKET_API_KEY}" ]] ; then
  echo "Packet api is empty"
  export PACKET_API_KEY="#{ENV['PACKET_API_KEY']}"
fi

if [[ -z "${PACKET_PROJECT_UUID}" ]] ; then
  echo "Packet project uuid is empty"
  export PACKET_PROJECT_UUID="#{ENV['PACKET_PROJECT_UUID']}"
fi

# vagrant cloud info
export VAGRANT_CLOUD_USER="elrey741"

if [[ -z "${VAGRANT_CLOUD_TOKEN}" ]] ; then
  echo "Vagrant cloud token is empty"
  export VAGRANT_CLOUD_TOKEN="#{ENV['VAGRANT_CLOUD_TOKEN']}" 
fi

# versioning for vagrant cloud
export MAJOR_RELEASE_VERSION=0
export MINOR_RELEASE_VERSION=0

# text info
if [[ -z "${PERSONAL_NUM}" ]] ; then
  echo "Vagrant cloud token is empty"
  export VAGRANT_CLOUD_TOKEN="#{ENV['VAGRANT_CLOUD_TOKEN']}" 
fi

if [[ -z "${TEXTBELT_KEY}" ]] ; then
  echo "Vagrant cloud token is empty"
  export VAGRANT_CLOUD_TOKEN="#{ENV['VAGRANT_CLOUD_TOKEN']}" 
fi
