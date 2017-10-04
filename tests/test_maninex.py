import os, shutil
import tempfile
import pytest
from maninex import maninex

# VERY lazy testing

CONF_CONTENT = '''
[directories]
extension_dir = none
json_dir = /usr/share/inox/extensions

[extensions]
cjpalhdlnbpafiamejdnhcphjbkeiagm
pkehgijcmpdhfbdbbnkijodmdjhbjlgp
egnjhciaieeiiohknchakcodbpgjnchh
'''


@pytest.fixture(scope='session')
def tmp_struct():
    # setup temporary home directory
    tmp_home = tempfile.mkdtemp()
    tmp_conf_file = os.path.join(tmp_home, 'maninex.conf')
    tmp_json_dir = tempfile.mkdtemp(dir=tmp_home)
    with open(tmp_conf_file, 'w') as file_:
        file_.write(CONF_CONTENT)

    # point maninex to temporary directory
    os.environ['HOME'] = tmp_home
    maninex.config_file = tmp_conf_file
    maninex.json_dir = tmp_json_dir
    yield
    shutil.rmtree(tmp_home)


def test_clean_mode(tmp_struct):
    try:
        maninex.clean_mode()
    except SystemExit:
        pass


def test_install_mode(tmp_struct):
    try:
        maninex.install_mode()
    except SystemExit:
        pass


def test_list_mode(tmp_struct):
    try:
        maninex.list_mode()
    except SystemExit:
        pass


def test_remove_mode(tmp_struct):
    try:
        maninex.remove_mode()
    except SystemExit:
        pass


def test_scan_mode(tmp_struct):
    try:
        maninex.scan_mode()
    except SystemExit:
        pass


def test_update_mode(tmp_struct):
    try:
        maninex.update_mode()
    except SystemExit:
        pass
