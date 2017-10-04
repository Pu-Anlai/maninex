Well, "manager" might be stretching it a bit. The idea is not having to manually look up and install updates when using a Chromium-like browser that doesn't use the WebStore plugin to handle these things. This is done by employing [this](https://developer.chrome.com/extensions/external_extensions#preferences) method which uses JSON preference files to point to local extension packages.

## Installation
    pip install maninex
Python 3.3 or higher required. Older Python 3 versions may work as well, but Python 2 won't. Instead of using pip to take care of the installation you can also just clone this repository and use the included cli.py file.

## Usage
```
usage: maninex [option]

options:
  -h, --help        show this help message and exit
  -c, --clean       clean up (i.e. remove) backed up extension files
  -i, --install     install all extensions that aren't already installed
  -l, --list        list all extensions and their current status
  -p, --print-skel  print the contents of a skeleton config file to stdout
  -r, --remove      remove all extensions that are installed but not in the
                    config file
  -s, --scan        scan for installed extensions not in the config file and
                    add them to the config file
  -u, --update      update all extensions

set up paths and extensions in maninex.conf
```

Maninex depends on a configuration file named "maninex.conf" for which it will look in three places: First in $XDG\_CONFIG\_HOME, then in $HOME/.config and finally in the same directory that the script is in. `maninex --print-skel` prints out a base config file with some basic instructions. Therefore, to get started you can run `maninex --print-skel > ~/.config/maninex.conf`.

Edit maninex.conf and add extensions by their ids under the [extension] header. You can use the scan option to add extensions you manually installed before (see below). To find out an extension's id, search for the it on the [Chrome WebStore](https://chrome.google.com/webstore/category/extensions). The final part of the extension page's URL is the id. For example, [this](https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm) is the url of uBlock Origin and its id is therefore "cjpalhdlnbpafiamejdnhcphjbkeiagm".
Every extension id should occupy one line under the [extension] header. Optionally you can prepend an identifier for the extension like this:
    uBlock Origin = cjpalhdlnbpafiamejdnhcphjbkeiagm

This is recommended as it will make messages more descriptive, for example `Extension "cjpalhdlnb…" installed.` will become `Extension "My Extension" installed.` 

Run `maninex -i` to install all the extensions in the config file. Run `maninex -u` to look up and download updates.

## Other functionality
### --clean
This will remove old extension files that were backed up during previous updates.

### --scan
Scan the extension directory and add all extensions to the config file that aren't included already.

### --remove
The opposite of scan. Remove all extensions that aren't included in the config file.
