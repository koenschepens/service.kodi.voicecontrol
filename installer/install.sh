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

mkdir .backup
sudo cp /Applications/Kodi.app/Contents/Resources/Kodi/addons/service.kodi.voicecontrol/*.config ./.backup 
sudo rm -R /Applications/Kodi.app/Contents/Resources/Kodi/addons/service.kodi.voicecontrol/
rm -v -R ../program/*.pyc
rm -R $serviceFolder/*.pyc
rsync -av --exclude='*.config' --exclude='build' --exclude='*.pyc' --exclude='installer' ../ $serviceFolder/

cp -Rv ./.backup/* /Applications/Kodi.app/Contents/Resources/Kodi/addons/service.kodi.voicecontrol/

if [ ! -f $serviceFolder/settings.config ] || [ "$1" == "-f" ]
	then
		echo "copying config"
		cp -v ../program/*.config $serviceFolder
fi

sudo chown -R $(whoami) $serviceFolder

sudo chmod -R 775 $serviceFolder

echo "Done"
