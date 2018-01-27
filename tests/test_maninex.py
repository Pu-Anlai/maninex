import os
import tempfile
import shutil
import configparser
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
def confix_struct():
    test_json_dir = tempfile.mkdtemp(prefix='mt_json_')
    test_ext_dir = tempfile.mkdtemp(prefix='mt_ext_')
    _, test_config_file = tempfile.mkstemp(prefix='mt_conf_')

    with open(test_config_file, 'w') as file_:
        file_.write(CONF_CONTENT)

    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = lambda option: option

    yield maninex.Configs(json_dir=test_json_dir, ext_dir=test_ext_dir,
                          config_file=test_config_file,
                          config=config.read(test_config_file))

    shutil.rmtree(test_json_dir)
    shutil.rmtree(test_ext_dir)
    os.remove(test_config_file)


def test_clean_mode():
    try:
        maninex.clean_mode()
    except SystemExit:
        pass


def test_install_mode():
    try:
        maninex.install_mode()
    except SystemExit:
        pass


def test_list_mode():
    try:
        maninex.list_mode()
    except SystemExit:
        pass


def test_remove_mode():
    try:
        maninex.remove_mode()
    except SystemExit:
        pass


def test_scan_mode():
    try:
        maninex.scan_mode()
    except SystemExit:
        pass


def test_update_mode():
    try:
        maninex.update_mode()
    except SystemExit:
        pass


def test_print_skel_mode():
    try:
        maninex.print_skel_mode()
    except SystemExit:
        pass
