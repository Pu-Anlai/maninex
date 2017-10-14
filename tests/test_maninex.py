import os
import sys
import shutil
import tempfile

# PYTHONPATH fix
parent_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(parent_path)

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
TMP_HOME = tempfile.mkdtemp()
# setup temporary home directory
tmp_conf_dir = os.path.join(TMP_HOME, '.config')
os.mkdir(tmp_conf_dir)
tmp_conf_file = os.path.join(tmp_conf_dir, 'maninex.conf')
tmp_json_dir = tempfile.mkdtemp(dir=TMP_HOME)
with open(tmp_conf_file, 'w') as file_:
    file_.write(CONF_CONTENT)

# point maninex to temporary directory
os.environ['HOME'] = TMP_HOME
from maninex import maninex

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


shutil.rmtree(TMP_HOME)
