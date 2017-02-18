import re
import configparser
import argparse
import os
import requests


def is_root():
    """Check if user is root."""
    if os.geteuid() == 0:
        return True


def get_existing_jsons():
    """Get a list of all extensions that are already referenced by json
    files."""
    json_list = os.listdir(JSON_DIR)
    for index, json in enumerate(json_list):
        json_list[index] = json.strip('.json')

    return json_list


def get_existing_folders():
    """Return a list of all plugin folders that are already present in
    EXT_DIR."""
    folder_list = []
    for entry in os.scandir(path=EXT_DIR):
        if entry.is_dir() is True and \
         len(entry.name) == 32 and \
         os.listdir(entry.path):
            folder_list.append(entry.name)

    return folder_list


def update_config_ext(ext_list):
    """Update the list of extensions in config with ext_list."""
    ext = dict.fromkeys(config.options('extensions'), None)
    new_ext = dict.fromkeys(ext_list, None)
    ext.update(new_ext)
    config['extensions'] = ext


def create_json(ext_id, filepath):
    """Create a json file in JSON_DIR that refers to ext_id and filepath."""
    filepath = os.path.abspath(filepath)
    filename = os.path.basename(filepath)
    version = re.findall(r'(\d[\d_]+)', filename)[0]
    version = version.replace('_', '.')
    json = os.path.join(JSON_DIR, ext_id) + '.json'
    with open(json, 'w+') as json_f:
        json_f.write('{\n')
        json_f.write('  "external_crw": "' + filepath + '",\n')
        json_f.write('  "external_version": "' + version + '",\n')
        json_f.write('}')


def get_url_request(ext_id):
    """Return a requests object for ext_id in the Chrome store. Return 'False'
    if extension doesn't exist."""
    url = 'https://clients2.google.com/service/update2/crx?response=redirect&'\
          'prodversion=48.0&x=id%3D{}%26installsource%3Dondemand%26uc'.format(
              ext_id
              )
    ext_r = requests.get(url)
    if not ext_r.url.rsplit('.', 1)[-1] == 'crx':
        return False

    return ext_r


def download_ext(ext_id, url_obj):
    """Handles requests object. Downloads an extension to EXT_DIR."""
    ext_path = os.path.join(EXT_DIR, ext_id)
    filename = url_obj.url.rsplit('/', 1)[-1]
    filepath = os.path.join(ext_path, filename)
    if not os.path.exists(ext_path):
        os.mkdir(ext_path)

    with open(filepath, 'wb') as ext_f:
        ext_f.write(url_obj.content)

    return filepath


def install_mode():
    """Install all extensions listed in config."""
    # if not is_root():
    #     print('Need to be root.')
    #     return

    ext_list = config.options('extensions')
    for ext_id in ext_list:
        if ext_id not in get_existing_jsons() or \
           ext_id not in get_existing_folders():
            ext_r = get_url_request(ext_id)
            if ext_r is False:
                print('Extension "{}" not found.'.format(ext_id))
            else:
                filepath = download_ext(ext_id, ext_r)
                create_json(ext_id, filepath)
                print('Extension "{}" installed.'.format(ext_id))
        else:
            print('Extension "{}" is already installed.'.format(ext_id))


argparser = argparse.ArgumentParser()
argparser.parse_args()

CONFIG_FILE = 'maninex.deb.conf'
config = configparser.ConfigParser(allow_no_value=True)
config.read(CONFIG_FILE)
# if directory strings have no trailing slashes, add them for consistency
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
ARGS = parser.parse_args()
args_count = list(vars(ARGS).values()).count(True)
# display help message if no arguments are supplied
if args_count == 0:
    parser.print_help()
# display error message if more than one argument is supplied
elif args_count > 1:
    print('only one argument at a time is accepted.')
