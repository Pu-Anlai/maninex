import os
import re
import tempfile
import shutil
import configparser
from threading import Thread
import pytest
from maninex import maninex

CONF_CONTENT = '''
[directories]
extension_dir = none
json_dir = /usr/share/inox/extensions

[extensions]
cjpalhdlnbpafiamejdnhcphjbkeiagm
pkehgijcmpdhfbdbbnkijodmdjhbjlgp
egnjhciaieeiiohknchakcodbpgjnchh
'''


@pytest.fixture(scope='module')
def config_struct():
    test_json_dir = tempfile.mkdtemp(prefix='mt_json_')
    test_ext_dir = tempfile.mkdtemp(prefix='mt_ext_')
    _, test_config_file = tempfile.mkstemp(prefix='mt_conf_')

    with open(test_config_file, 'w') as file_:
        file_.write(CONF_CONTENT)

    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = lambda option: option
    config.read(test_config_file)

    yield maninex.Configs(json_dir=test_json_dir, ext_dir=test_ext_dir,
                          config_file=test_config_file,
                          config=config)

    shutil.rmtree(test_json_dir)
    shutil.rmtree(test_ext_dir)
    os.remove(test_config_file)


def test_file_getters(config_struct):
    """Test get_* functions with no installed extensions."""
    installed_jsons = maninex.get_existing_jsons(config_struct.json_dir)
    installed_folders = maninex.get_existing_folders(config_struct.ext_dir)
    assert len(installed_jsons) == 0
    assert len(installed_folders) == 0
    for ext_ref in maninex.get_exts_from_config(config_struct.config):
        assert not maninex.is_installed(config_struct,
                                        ext_ref.idstr)


def test_install_extensions(config_struct):
    """Try installing extensions and check if the get_ functions return
    appropriate results."""
    exts = maninex.get_exts_from_config(config_struct.config)

    threads = []
    for ext_ref in exts:
        ext_thread = Thread(target=maninex.process_extension_install,
                            args=(config_struct, ext_ref))
        ext_thread.start()
        threads.append(ext_thread)

    for ext_thread in threads:
        ext_thread.join()

    for ext_ref in exts:
        assert maninex.is_installed(config_struct,
                                    ext_ref.idstr)
        local_version = maninex.get_local_version(config_struct.ext_dir,
                                                  ext_ref.idstr)
        online_version = maninex.ExtensionOnline(config_struct,
                                                 ext_ref.idstr).version
        assert local_version == online_version


def test_update_extensions(config_struct):
    """Assume all extensions are outdated and try updating them."""
    exts = maninex.get_exts_from_config(config_struct.config)

    for ext_ref in exts:
        ext_obj = maninex.ExtensionOnline(config_struct, ext_ref.idstr)
        # rename the extension files, so they appear out of date
        filepath = ext_obj.ext_path_file
        new_filename = re.sub(r'(\d[\d_]+)', 'foo', os.path.basename(filepath))
        new_filepath = os.path.join(os.path.dirname(filepath), new_filename)
        os.rename(filepath, new_filepath)

    threads = []
    dir_list = maninex.get_existing_folders(config_struct.ext_dir)
    for ext_ref in exts:
        ext_thread = Thread(target=maninex.process_extension_update,
                            args=(config_struct, ext_ref, dir_list))
        ext_thread.start()
        threads.append(ext_thread)

    for ext_thread in threads:
        ext_thread.join()

    for ext_ref in exts:
        assert maninex.is_installed(config_struct,
                                    ext_ref.idstr)
        ext_obj = maninex.ExtensionOnline(config_struct, ext_ref.idstr)
        local_version = maninex.get_local_version(config_struct.ext_dir,
                                                  ext_ref.idstr)
        assert local_version == ext_obj.version
        # assume there's an .old backup file for every extension in their
        # respective directory
        for f in os.scandir(ext_obj.ext_path):
            if f.name.endswith('.foo.old'):
                break
        else:
            raise FileNotFoundError
