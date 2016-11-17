# Arma3Sync Repository Updater
A Python Python-powered Mod Updater for Arma3Sync Repositorys with steam workshop integration.

## Features
* Updating mods
* organizing said mods

## Requirements
* [python3](https://www.python.org/downloads/)
* [argparse](https://pypi.python.org/pypi/argparse)
* [gitpython](https://pypi.python.org/pypi/GitPython)
* [glob2](https://pypi.python.org/pypi/glob2)
* [pyunpack](https://pypi.python.org/pypi/pyunpack)
* [requests](https://pypi.python.org/pypi/requests)
* [python-magic](https://pypi.python.org/pypi/patool)
* [steamcmd](https://developer.valvesoftware.com/wiki/SteamCMD#Downloading_SteamCMD)
* [Arma3Sync](https://forums.bistudio.com/topic/152942-arma3sync-launcher-and-addons-synchronization-software-for-arma-3/)
* [Java](https://www.java.com)

## Installation
First of all you need Python3 (not Python2).
### Python
#### Arch Linux
`pacman -S python3 pip3`
#### Ubuntu/Debian
`apt install python3 pip3`
#### RedHat/CentOS
`yum install python3 pip3`
Then install the required packages from PyPi
### PyPi
`sudo pip install -r requirements.txt`

And then SteamCMD. For more help visit the [SteamCMD wiki](https://developer.valvesoftware.com/wiki/SteamCMD).
### SteamCMD
#### Arch Linux
`pacman -S steamcmd`
#### Ubuntu/Debian
`apt install steamcmd`
#### RedHat/CentOS
`yum install steamcmd`
#### Manual
You need to install `lib32gcc1` too

`curl -sqL 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz' | tar zxvf -`

### Arma3Sync
Now _Arma3Sync_ to make the repositorys but you can also use something else like [Swifty](https://getswifty.net/) (ony available on Windows).

Install Java
#### Arch Linux
`pacman -S java`
#### Ubuntu/Debian
`apt install java`
#### RedHat/CentOS
`yum install java`

Get _Arma3Sync_ from [armaholic.com](http://www.armaholic.com/page.php?id=22199) or from [sonsofexiled.fr](http://www.sonsofexiled.fr/wiki/index.php/ArmA3Sync_Wiki_English). You can also use SVN to get the source `svn://www.sonsofexiled.fr/repository/ArmA3Sync/releases`.


## Usage
`a3s-repo-updater.py --add`

`a3s-repo-updater.py --remove`

`a3s-repo-updater.py --update`

## License
A3S Repository Updater is licensed under the [GNU license](LICENSE).
