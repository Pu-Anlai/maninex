Well, "manager" might be stretching it a bit. The idea is not having to
manually look up and install updates when using a Chromium-like browser
that doesn't use the WebStore plugin to handle these things. This is
done by employing
`this <https://developer.chrome.com/extensions/external_extensions#preferences>`__
method which uses JSON preference files to point to local extension
packages.

Installation
------------

If you're on ArchLinux, you can install maninex via the Arch User Repository. Use your favorite AUR helper or simply git:

::
    
    git clone https://aur.archlinux.org/maninex.git
    cd maninex
    makepkg -sri

On other distros you can use pip to install maninex and handle dependencies (one: requests).
::

    pip install maninex

Maninex won't run on Python versions lower than 3.5.

Usage
-----

::

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

Maninex depends on a configuration file named "maninex.conf" for which
it will look in three places: First in $XDG\_CONFIG\_HOME, then in
$HOME/.config and finally in the same directory that the script is in.
``maninex --print-skel`` prints out a base config file with some basic
instructions. Therefore, to get started you can run
``maninex --print-skel > ~/.config/maninex.conf``.

Edit maninex.conf and add extensions by their ids under the [extension]
header. You can use the scan option to add extensions you manually
installed before (see below). To find out an extension's id, search for
the it on the `Chrome
WebStore <https://chrome.google.com/webstore/category/extensions>`__.
The final part of the extension page's URL is the id. For example,
`this <https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm>`__
is the url of uBlock Origin and its id is therefore
"cjpalhdlnbpafiamejdnhcphjbkeiagm". Every extension id should occupy one
line under the [extension] header. Optionally you can prepend an
identifier for the extension like this:
``uBlock Origin = cjpalhdlnbpafiamejdnhcphjbkeiagm``

This is recommended as it will make messages more descriptive, for
example ``Extension "cjpalhdlnb…" installed.`` will become
``Extension "uBlock Origin" installed.``

Run ``maninex -i`` to install all the extensions in the config file. Run
``maninex -u`` to look up and download updates.

Other functionality
-------------------

--clean
~~~~~~~

This will remove old extension files that were backed up during previous
updates.

--list
~~~~~~

List all extensions in the config file and whether or not they are
installed already.

--scan
~~~~~~

Scan the extension directory and add all extensions to the config file
that aren't included already.

--remove
~~~~~~~~

The opposite of scan. Remove all extensions that aren't included in the
config file.
