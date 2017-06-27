# TODO: use get_exts_from_config for handling extensions not the direct values from the config
import re
import configparser
import argparse
import os
import requests
import textwrap
from collections import namedtuple

term_width = os.get_terminal_size().columns

ExtRef = namedtuple('ExtensionReference', ['name', 'idstr'])


class ExtensionOnline(object):
    """Holds relevant information about an extension including a requests
    object pointing to its online location."""
    def __init__(self, ext_id):
        self.ext_id = ext_id
        self.requests_url = 'https://clients2.google.com/service/update2/crx?'\
            'response=redirect&prodversion=48.0&x=id%3D{}%26installsource%3Do'\
            'ndemand%26uc'.format(ext_id)
        self.requests_object = requests.get(self.requests_url)
        self.url = self.requests_object.url
        self.exists = self.check_exists()
        self.filename = self.url.rsplit('/', 1)[-1]
        self.version = self.get_version()
        self.ext_path = os.path.abspath(os.path.join(EXT_DIR, self.ext_id))
        self.ext_path_file = os.path.join(self.ext_path, self.filename)
        self.json_path_file = os.path.abspath(os.path.join(JSON_DIR,
                                              self.ext_id + '.json'))

    def check_exists(self):
        if not self.url.rsplit('.', 1)[-1] == 'crx':
            return False

    def get_version(self):
        version = re.findall(r'(\d[\d_]+)', self.filename)[0]
        version = version.replace('_', '.')
        return version


def is_root():
    """Check if user is root."""
    if os.geteuid() == 0:
        return True


def mline_print(msg):
    """Print dedented version of multiline text"""
    msg.replace('\n', '')
    msg = re.sub('\s{2,}', ' ', msg)
    print(textwrap.fill(msg, width=term_width))


def get_existing_jsons():
    """Get a list of all extensions that are already referenced by json
    files."""
    try:
        json_list = os.listdir(JSON_DIR)
        for index, json in enumerate(json_list):
            json_list[index] = json.strip('.json')
    except FileNotFoundError:
        json_list = None

    return json_list


def get_existing_folders():
    """Return a list of all plugin folders that are already present in
    EXT_DIR."""
    folder_list = []
    try:
        for entry in os.scandir(path=EXT_DIR):
            if entry.is_dir() is True and \
             len(entry.name) == 32 and \
             os.listdir(entry.path):
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
    files = os.listdir(os.path.abspath(os.path.join(EXT_DIR, ext_id)))
    for filename in files:
        if filename[-3:] == 'crx':
            version = re.findall(r'(\d[\d_]+)', filename)[0]
            version = version.replace('_', '.')
            return version
    return None


def create_json(json_file, filepath, version):
    """Create a json file in JSON_DIR that refers to ext_id and filepath."""
    with open(json_file, 'w+') as json_f:
        json_f.write('{\n')
        json_f.write('  "external_crw": "' + filepath + '",\n')
        json_f.write('  "external_version": "' + version + '"\n')
        json_f.write('}')


def download_ext(ext_path, ext_path_file, ext_content):
    """Downloads an extension to EXT_DIR."""
    if not os.path.exists(ext_path):
        os.mkdir(ext_path)

    with open(ext_path_file, 'wb') as ext_f:
        ext_f.write(ext_content)


def get_exts_from_config():
    """Create a list of named tuples for all extensions in config."""
    ext_list = []
    for key, value in config['extensions'].items():
        if value == None:
            # if no name has been specified for the extension just use a
            # shortened version of the id
            ext_list.append(ExtRef(name=key[0:11], idstr=key))
        else:
            ext_list.append(ExtRef(name=key, idstr=value))
    return ext_list


def create_directories():
    for directory in [JSON_DIR, EXT_DIR]:
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass


def is_installed(ext_id):
    """Check if extension with ext_id is installed."""
    if ext_id in get_existing_jsons() and \
       ext_id in get_existing_folders():
            return True


def install_extension(ext_obj):
    # if ext_obj.ext_id not in get_existing_folders():
    download_ext(ext_obj.ext_path,
                 ext_obj.ext_path_file,
                 ext_obj.requests_object.content)
    # if ext_obj.ext_id not in get_existing_jsons():
    create_json(ext_obj.json_path_file,
                ext_obj.ext_path_file,
                ext_obj.version)


def update_extension(ext_obj):
    """Update extension in ext_obj and rename old extension file."""
    install_extension(ext_obj)
    files = os.listdir(os.path.abspath(os.path.join(EXT_DIR, ext_obj.ext_id)))
    for filename in files:
        if filename != ext_obj.filename and \
          filename[-3:] != 'old':
            f = os.path.abspath(os.path.join(ext_obj.ext_path, filename))
            os.rename(f, f + '.old')


def install_mode():
    """Install all extensions listed in config."""
    if not is_root():
        mline_print("""You're not running this script as root. If you don't have
                       write access to the paths you have set in your config file,
                       this operation will fail.""")

    create_directories()

    for ext_ref in get_exts_from_config():
        ext_obj = ExtensionOnline(ext_ref.idstr)

        if not is_installed(ext_ref.idstr):
            if ext_obj.exists is False:
                print('Extension "{}" not found.'.format(ext_ref.name))
            else:
                install_extension(ext_obj)
                print('Extension "{}" installed.'.format(ext_ref.name))
        else:
            print('Extension "{}" is already installed.'.format(ext_ref.name))


def update_mode():
    """Update all extensions that are in config and are also present in the
    extension directory."""
    dir_list = get_existing_folders()
    for ext_ref in get_exts_from_config():
        if ext_ref.idstr in dir_list:
            ext_obj = ExtensionOnline(ext_ref.idstr)
            try:
                local_ver = get_local_version(ext_ref.idstr)
                if ext_obj.version != local_ver:
                    update_extension(ext_obj)
                    print('Extension {} updated.'.format(ext_ref.name))
                else:
                    print('Extensions {} up-to-date.'.format(ext_ref.name))
            except FileNotFoundError:
                update_extension(ext_obj)
                print('Extension {} updated.'.format(ext_ref.name))
        else:
            print('Extension {} in config but not installed. Skipping...')


def scan_mode():
    jsons = get_existing_jsons()
    exts = get_exts_from_config()
    exts_ids = [exts[ext].idstr for ext in range(0, len(exts))]
    for ext_id in jsons:
        if ext_id not in exts_ids:
            config['extensions'].update({ext_id: None})
    config.write()


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'maninex.deb.conf')
config = configparser.ConfigParser(allow_no_value=True)
config.read(CONFIG_FILE)
JSON_DIR = config['directories']['json_dir']
EXT_DIR = config['directories']['extension_dir']

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--update', action='store_true',
                    help='update all extensions in the config file')
parser.add_argument('-s', '--scan', action='store_true',
                    help='scan the json directory and add all existing \
                            extensions to the config file.')
parser.add_argument('-i', '--install', action='store_true',
                    help="install all extensions in the config file that aren't \
                            already installed.")
args = parser.parse_args()
args_count = list(vars(args).values()).count(True)
# display help message if no arguments are supplied
if args_count == 0:
    parser.print_help()
# display error message if more than one argument is supplied
elif args_count > 1:
    print('Only one argument at a time is supported.')
elif args.install:
    install_mode()
elif args.scan:
    print('scan mode')
elif args.update:
    update_mode()
