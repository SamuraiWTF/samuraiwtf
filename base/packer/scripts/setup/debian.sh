#!/usr/bin/env bash

set -euo pipefail
set -x

# all vars
alg='sha512'
verAlg="$(echo ${alg} | tr '[:lower:]' '[:upper:]')SUMS"
verAlgSig="${verAlg}.sign"
ARCH='amd64'
gpgKeyUrl='https://www.debian.org/CD/verify'
keyDistance='3'
debianKeyringUrl='keyring.debian.org/'
secretFileFullPath="${HOME}/src/mine/secrets/access_data"
curl='curl -fsSL'

## all urls
#initial url
downloadUrl="$(curl -sSL https://www.debian.org/CD/netinst/ | grep href | grep cdimage | grep -v torrent | grep -o "<a.*>$ARCH<" | cut -d '"' -f 2)"
echo "${downloadUrl}"
# base url
baseUrl="$(echo "${downloadUrl}" | rev | cut -d '/' -f 2- | rev)"
# shasum url
shasumUrl="${baseUrl}/${verAlg}"
# shasum url signature
shaSigUrl="${shasumUrl}.sign"



# Creating array of download urls
urlz=( "${shasumUrl}" "${shaSigUrl}" )

# downloading all urls
for i in "${urlz[@]}" ; do
  fileName="$(echo "${i}" | rev | cut -d '/' -f 1 | rev)"
  cmdz="curl -sSL -o $fileName ${i}"
  echo -e "Executing command:\n${cmdz}"
  $cmdz
done

# getting gpg key name
keyName="$(curl -s $gpgKeyUrl | grep -B $keyDistance "Debian CD signing key" | tail -n $keyDistance | grep pub | cut -d '/' -f 2 | cut -d ' ' -f 1)"

gpg --keyserver $debianKeyringUrl --recv-key $keyName &> /dev/null

namez="samuraiwtf-base_box"

if [[ -f $secretFileFullPath ]] ; then
	hashiName=$(grep vagrant_cloud $secretFileFullPath | cut -d ':' -f 2)
	vagrant_cloud_token=$(grep vagrant_cloud $secretFileFullPath | cut -d ':' -f 3-)
elif [[ $CIRCLECI ]] ; then
	hashiName="${VAGRANT_CLOUD_USER}"
	vagrant_cloud_token="${VAGRANT_CLOUD_TOKEN}"
elif [[ "$(whoami)" == 'vagrant' ]] ; then
  hashiName="${VAGRANT_CLOUD_USER}"
	vagrant_cloud_token="${VAGRANT_CLOUD_TOKEN}"
fi

if [[ ! -z $hashiName ]]; then
	namez="${hashiName}/${namez}"
	vagrantBoxUrl="https://app.vagrantup.com/$namez"
	if curl -sSL $vagrantBoxUrl | grep 'false' 1> /dev/null ; then
		vm_version='0.0.1'
	else
		currentVersion=$($curl $vagrantBoxUrl | jq '{versions}[][0]["version"]' | cut -d '"' -f 2)
		if [[ $CIRCLECI ]] ; then
			patch_release_version=$(( $(echo $currentVersion | cut -d '.' -f 3) + 1 ))
			vm_version="${MAJOR_RELEASE_VERSION}.${MINOR_RELEASE_VERSION}.${patch_release_version}"
		else
			echo -e "The current version is $currentVersion, what version would you like?\nPlease keep similar formatting as the current example."
			read -r vm_version
		fi
	fi
fi



if gpg --verify "${verAlgSig}" "${verAlg}" &>/dev/null  ; then

  currentISOVersion=$(echo "${downloadUrl}" | rev | cut -d '/' -f 1 | rev)
  currentHash=$(grep "${currentISOVersion}" "${verAlg}" | cut -d ' ' -f 1)
  echo "Verified shasum is genuine"

  rm "${verAlg}" "${verAlgSig}"

  printf '{"iso_url":"%s","iso_checksum_type":"%s","iso_checksum":"%s","vagrant_box_name":"%s","vm_version":"%s","vagrant_cloud_token":"%s"}\n' "$downloadUrl" "$alg" "$currentHash" "$namez" "$vm_version" "$vagrant_cloud_token" | jq . | tee variables.json
else
  echo "Bad file signing exiting now"
  exit 2
fi
