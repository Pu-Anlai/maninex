#!/usr/bin/env python3

import re
import os
import sys
import requests
import textwrap
from collections import namedtuple
from configparser import ConfigParser
from argparse import ArgumentParser
from shutil import rmtree
from threading import Thread

try:
    term_width = os.get_terminal_size().columns
except OSError:
    # OSError occurs when not running from real terminal (e.g. when testing)
    term_width = 80

ExtRef = namedtuple('ExtensionReference', ['name', 'idstr'])


class ExtensionOnline(object):
    """Holds relevant information about an extension including a requests
    object pointing to its online location."""
    def __init__(self, ext_id):
        self.ext_id = ext_id
        self.requests_url = (
                'https://clients2.google.com/service/update2/crx?response=redi'
                'rect&prodversion=48.0&x=id%3D{}%26installsource%3Dondemand%26'
                'uc'.format(ext_id))
        self.requests_object = requests.get(self.requests_url)
        self.url = self.requests_object.url
        self.exists = self.check_exists()
        self.filename = self.url.rsplit('/', 1)[-1]
        self.version = self.get_version()
        self.ext_path = os.path.join(ext_dir, self.ext_id)
        self.ext_path_file = os.path.join(self.ext_path, self.filename)
        self.json_path_file = os.path.abspath(os.path.join(json_dir,
                                              self.ext_id + '.json'))

    def check_exists(self):
        if not self.url.rsplit('.', 1)[-1] == 'crx':
            return False

    def get_version(self):
        version = re.findall(r'(\d[\d_]+)', self.filename)[0]
        version = version.replace('_', '.')
        return version


def get_real_path(path):
    """Get absolute expanded path for path and make sure to use user folders
    when running as root."""
    real_user = os.getenv('SUDO_USER') or os.getenv('USER')
    if path.startswith('~'):
        return os.path.abspath(path.replace('~', '/home/{}'.format(real_user)))
    elif path.startswith('/root'):
        return os.path.abspath(path.replace('/root',
                               '/home/{}'.format(real_user)))
    else:
        return os.path.abspath(path)


def check_folders(perm):
    """Check if user has the permissions perm for the directories in the config
    file. Exit if they don't."""
    if not (os.path.exists(ext_dir) and os.path.exists(json_dir)):
        mline_print("""One or more paths provided in maninex.conf could not be
                found.""", file=sys.stderr)
        sys.exit(1)
    elif not (os.access(ext_dir, perm) and os.access(json_dir, perm)):
        mline_print("""You don't have the necessary permissions for this
                operation.""", file=sys.stderr)
        sys.exit(1)


def adapt_owner(target):
    """Change owner of target to match the owner of its parent directory."""
    par_stat = os.stat(os.path.dirname(target))
    os.chown(target, par_stat.st_uid, par_stat.st_gid)


def mline_print(msg, **kwargs):
    """Print dedented version of multiline text"""
    msg.replace('\n', '')
    msg = re.sub('\s{2,}', ' ', msg)
    print(textwrap.fill(msg, width=term_width), **kwargs)


def get_existing_jsons():
    """Get a list of all extensions that are already referenced by json
    files."""
    try:
        json_list = os.listdir(json_dir)
        for index, json in enumerate(json_list):
            json_list[index] = json[:-5]
    except FileNotFoundError:
        json_list = []

    return json_list


def get_existing_folders():
    """Return a list of all plugin folders that are already present in
    ext_dir."""
    folder_list = []
    try:
        for entry in os.scandir(path=ext_dir):
            if (entry.is_dir() is True and
                    len(entry.name) == 32 and
                    os.listdir(entry.path)):
                folder_list.append(entry.name)
    except FileNotFoundError:
        pass

    return folder_list


def update_config_ext(ext_list):
    """Update the list of extensions in config with ext_list."""
    ext = dict.fromkeys(config['extensions'], None)
    new_ext = dict.fromkeys(ext_list, None)
    ext.update(new_ext)
    config['extensions'] = ext


def get_local_version(ext_id):
    files = os.listdir(os.path.join(ext_dir, ext_id))
    for filename in files:
        if filename[-3:] == 'crx':
            version = re.findall(r'(\d[\d_]+)', filename)[0]
            version = version.replace('_', '.')
            return version
    return None


def create_json(json_file, filepath, version):
    """Create a json file in json_dir that refers to ext_id and filepath."""
    with open(json_file, 'w+') as j_file:
        j_file.write('{\n')
        j_file.write('  "external_crx": "' + filepath + '",\n')
        j_file.write('  "external_version": "' + version + '"\n')
        j_file.write('}')

    adapt_owner(json_file)


def download_ext(ext_path, ext_path_file, ext_content):
    """Downloads an extension to ext_dir."""
    if not os.path.exists(ext_path):
        os.mkdir(ext_path)
        adapt_owner(ext_path)

    with open(ext_path_file, 'wb') as ep_file:
        ep_file.write(ext_content)

    adapt_owner(ext_path_file)


def get_exts_from_config():
    """Create a list of named tuples for all extensions in config."""
    for key, value in config['extensions'].items():
        if value is None:
            # if no name has been specified for the extension just use a
            # shortened version of the id
            yield ExtRef(name=key[0:11], idstr=key)
        else:
            yield ExtRef(name=key, idstr=value)


def is_installed(ext_id):
    """Check if extension with ext_id is installed."""
    if ext_id in get_existing_jsons() and ext_id in get_existing_folders():
            return True


def install_extension(ext_obj):
    download_ext(ext_obj.ext_path,
                 ext_obj.ext_path_file,
                 ext_obj.requests_object.content)
    create_json(ext_obj.json_path_file,
                ext_obj.ext_path_file,
                ext_obj.version)


def process_extension_install(ext_ref):
    if not is_installed(ext_ref.idstr):
        ext_obj = ExtensionOnline(ext_ref.idstr)
        if ext_obj.exists is False:
            print('Extension "{}" not found.'.format(ext_ref.name))
        else:
            install_extension(ext_obj)
            print('Extension "{}" installed.'.format(ext_ref.name))
    else:
        print('Extension "{}" is already installed.'.format(ext_ref.name))


def update_extension(ext_obj):
    """Update extension in ext_obj and rename old extension file."""
    install_extension(ext_obj)
    files = os.listdir(os.path.join(ext_dir, ext_obj.ext_id))
    for filename in files:
        if (filename != ext_obj.filename and not filename.endswith('.old')):
            f = os.path.join(ext_obj.ext_path, filename)
            os.rename(f, f + '.old')


def process_extension_update(ext_ref, dir_list):
    """Look up and apply updates for a single extension. Afterwards, print the
    result."""
    if ext_ref.idstr in dir_list:
        ext_obj = ExtensionOnline(ext_ref.idstr)
        try:
            local_ver = get_local_version(ext_ref.idstr)
            if ext_obj.version != local_ver:
                update_extension(ext_obj)
                print('Extension "{}" updated.'.format(ext_ref.name))
            else:
                print('Extension "{}" up-to-date.'.format(ext_ref.name))
        except FileNotFoundError:
            update_extension(ext_obj)
            print('Extension "{}" updated.'.format(ext_ref.name))
    else:
        print('Extension "{}" in config but not installed. '
              'Skipping...'.format(ext_ref.name))


def clean_mode():
    """Remove all *.old files."""
    check_folders(os.W_OK)

    for ext_ref in get_exts_from_config():
        path = os.path.join(ext_dir, ext_ref.idstr)
        try:
            for f in os.scandir(path):
                if f.name.endswith('.old'):
                    os.remove(os.path.abspath(f.path))
                    print('File "{}" of Extension "{}" removed.'.format(
                        f.name, ext_ref.name
                        ))
        except FileNotFoundError:
            pass


def install_mode():
    """Install all extensions listed in config."""
    check_folders(os.W_OK)

    threads = []
    for ext_ref in get_exts_from_config():
        ext_thread = Thread(target=process_extension_install, args=(ext_ref, ))
        ext_thread.start()
        threads.append(ext_thread)

    for ext_thread in threads:
        ext_thread.join()


def list_mode():
    check_folders(os.R_OK)
    installed_jsons = get_existing_jsons()
    installed_folders = get_existing_folders()

    for ext_ref in get_exts_from_config():
        if (ext_ref.idstr in installed_jsons and
                ext_ref.idstr in installed_folders):
            print('{}: Installed.'.format(ext_ref.name))
        else:
            print('{}: Not installed.'.format(ext_ref.name))


def remove_mode():
    """Remove json file and ext directory for files that are no longer in
    config_file."""
    check_folders(os.W_OK)
    ext_ids = [ext_ref.idstr for ext_ref in get_exts_from_config()]

    for folder in get_existing_folders():
        if folder not in ext_ids:
            rmtree(os.path.join(ext_dir, folder))
            print('Extension folder {} removed.'.format(folder))

    for json in get_existing_jsons():
        if json not in ext_ids:
            filename = json + '.json'
            os.remove(os.path.join(json_dir, filename))
            print('JSON file {} removed.'.format(filename))


def scan_mode():
    """Scan for already installed files and add them to config_file."""
    check_folders(os.R_OK)
    jsons = get_existing_jsons()
    exts = list(get_exts_from_config())
    exts_ids = [exts[ext].idstr for ext in range(0, len(exts))]

    for ext_id in jsons:
        if ext_id not in exts_ids:
            config['extensions'].update({ext_id: None})
            print('Extension {} added.'.format(ext_id[0:11] + '…'))
    with open(config_file, 'w') as c_file:
        config.write(c_file)


def update_mode():
    """Update all extensions that are in config and are also present in the
    extension directory."""
    check_folders(os.W_OK)

    dir_list = get_existing_folders()
    threads = []
    for ext_ref in get_exts_from_config():
        ext_thread = Thread(target=process_extension_update,
                            args=(ext_ref, dir_list))
        ext_thread.start()
        threads.append(ext_thread)

    for ext_thread in threads:
        ext_thread.join()


def get_config_location():
    """Return the location of the config file. A file in $XDG_CONFIG_HOME takes
    precedence over a file present in the script directory."""
    xdg_config_home = (os.getenv('XDG_CONFIG_HOME') or
                       os.path.join(os.getenv('HOME'), '.config'))
    xdg_config_file = os.path.join(get_real_path(xdg_config_home),
                                   'maninex.conf')
    script_dir_file = os.path.join(os.path.dirname(get_real_path(__file__)),
                                   'maninex.conf')

    if os.path.exists(xdg_config_file):
        return xdg_config_file
    elif os.path.exists(script_dir_file):
        return script_dir_file
    else:
        mline_print("""maninex depends on a config file named maninex.conf.
        This file can be located either in your $XDG_CONFIG_HOME directory or
        in the location of maninex.py.""")
        sys.exit(1)


def main():
    """Main function to be run from CLI."""
    # display help message if no arguments are supplied
    if args_count == 0:
        parser.print_help()
    # display error message if more than one argument is supplied
    elif args_count > 1:
        print('Only one argument at a time is supported.')
    elif args.clean:
        clean_mode()
    elif args.install:
        install_mode()
    elif args.list:
        list_mode()
    elif args.remove:
        remove_mode()
    elif args.scan:
        scan_mode()
    elif args.update:
        update_mode()


config_file = get_config_location()
config = ConfigParser(allow_no_value=True)
# don't process option names in the config file, i.e. don't convert them to
# lowercase
config.optionxform = lambda option: option
config.read(config_file)

json_dir = get_real_path(config['directories']['json_dir'])
ext_dir = get_real_path(config['directories']['extension_dir'])

parser = ArgumentParser(usage='%(prog)s [option]',
                        epilog='set up paths and extensions in maninex.conf')
parser._optionals.title = 'options'
parser.add_argument('-c', '--clean', action='store_true',
                    help='clean up (i.e. remove) backed up extension files')
parser.add_argument('-i', '--install', action='store_true',
                    help="""install all extensions that aren't already
                    installed""")
parser.add_argument('-l', '--list', action='store_true',
                    help='''list all extensions and their current status''')
parser.add_argument('-r', '--remove', action='store_true',
                    help='''remove all extensions that are installed but not
                    listed''')
parser.add_argument('-s', '--scan', action='store_true',
                    help='''scan for installed unlisted extensions and add them
                    to the config file''')
parser.add_argument('-u', '--update', action='store_true',
                    help='update all extensions')
args = parser.parse_args()
args_count = list(vars(args).values()).count(True)
