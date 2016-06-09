import os
import platform


if platform.system() == 'Darwin':
    ROOT_PATH = '/Users/user/Projects/alfred'
else:
    ROOT_PATH = '/home/pi/Projects/alfred/just-another-AI/'

TESTER_PATH = os.path.join(ROOT_PATH, 'tester')
MAC_PATH = os.path.join(ROOT_PATH, 'current_mac_version')
PI_PATH = os.path.join(ROOT_PATH, 'current_pi_version')

def test_builder(fname):
    return os.path.join(TESTER_PATH, fname)

def mac_builder(fname):
    return os.path.join(MAC_PATH, fname)

def pi_builder(fname):
    return os.path.join(PI_PATH, fname)



