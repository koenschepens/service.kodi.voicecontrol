#!/bin/bash

serviceFolder="~/.kodi/addons/service.kodi.voicecontrol"

if [ ! -d $serviceFolder ]
	then
		serviceFolder="/Applications/Kodi.app/Contents/Resources/Kodi/addons/service.kodi.voicecontrol"
fi

if [ ! -d $serviceFolder ]
	then
		echo "creating $serviceFolder"
		mkdir $serviceFolder
fi

rm -v -R ../program/*.pyc
rsync -av --exclude='*.config' --exclude='*.pyc' ../program/ $serviceFolder/



if [ ! -f $serviceFolder/settings.config ] || [ "$1" == "-f" ]
	then
		echo "copying config"
		cp -v ../program/*.config $serviceFolder
fi

sudo chown -R $(whoami) $serviceFolder

sudo chmod -R 775 $serviceFolder

echo "Done"
