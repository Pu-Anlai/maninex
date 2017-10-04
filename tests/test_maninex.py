from maninex import maninex

# VERY lazy testing


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
