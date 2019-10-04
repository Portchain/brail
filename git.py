import subprocess
import os
import re
from subprocess import call

DEVNULL = open(os.devnull, 'w')

def get_repo_dir():
    return subprocess.Popen(
        ['git', 'rev-parse', '--show-toplevel'],
        stdout=subprocess.PIPE, stderr=DEVNULL).communicate()[0].rstrip().decode('utf-8')

def get_current_branch():
    try:
        head_file = os.path.join(get_repo_dir(), '.git', 'HEAD')
        head_ref = open(head_file, 'r').read()
        match = re.match("ref: refs/heads/(.*)", head_ref)
        if match is None:
            return None
        else:
            cur_branch = match.group(1)
            return cur_branch
    except:
        return None

def add_file(path):
    return call_git(["add", path])

def call_git(argv):
    return call(["git"] + argv)