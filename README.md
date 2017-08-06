Well, "manager" might be stretching it a bit. The idea is not having to manually look up and install updates when using a Chromium-like browser that doesn't use the WebStore plugin to handle these things. This is done by employing [this](https://developer.chrome.com/extensions/external_extensions#preferences) method which uses JSON preference files to point to local extension packages.

## Usage
You'll need Python3 and the requests module.

Put the id of all extensions you want to use under the [extensions] header in maninex.conf. If you've manually installed extensions before (using the JSON file method), you can add them to the config file by running `./maninex.py --scan`.
`./maninex.py --install` will download and install all extensions that are listed in maninex.conf. Run `./maninex.py --update` every once in a while to look up and install updates.

Optionally you can give each extension an identifier by using the `key = value` syntax of the config file, where key represents the identifier and value the extension id. E.g.:
`My Extension = aaaaaaaaaabbbbbbbbbbcccccccccc`

The only effect this has is replacing the id in output messages. So `Extension "aaaaaaaaaa…" installed.` will become `Extension "My Extension" installed.` 

There's some other basic functionality:
```
options:
  -h, --help     show this help message and exit
  -c, --clean    clean up (i.e. remove) backed up extension files
  -i, --install  install all extensions that aren't already installed
  -l, --list     list all extensions and their current status
  -r, --remove   remove all extensions that are installed but not listed
  -s, --scan     scan for installed unlisted extensions and add them to the
                 config file
  -u, --update   update all extensions
```
