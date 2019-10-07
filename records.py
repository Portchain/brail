import binascii
import os
from os.path import expanduser, join
from git import get_repo_dir, show_file
from errors import ManagedException

def generate_record_id():
    return binascii.b2a_hex(os.urandom(20)).decode('utf8')

# Buffer may be null, then nothing will be written
def write_record(record_dir_path, record_id, buffer):
    filename = record_id
    file_path = join(record_dir_path, filename)
    with open(file_path, 'w') as f:
        if buffer:
            f.write(buffer)
            os.fsync(f)
    return file_path

# record_fields is dict or None
def create_record(conf, record_fields):
    repo_dir = get_repo_dir()
    if repo_dir is None:
        raise ManagedException("No git repo found")
    
    if conf['record_dir'] is None:
        raise ManagedException("Must specify record_dir in conf")
    record_dir_path = join(repo_dir, conf['record_dir'])

    record_id = generate_record_id()
    if record_fields is not None:
        record_buffer = record_fields.get('type', 'type') + ': ' + record_fields.get('description', '')
    else:
        record_buffer = None
    record_path = write_record(record_dir_path, record_id, record_buffer)
    return record_id, record_path

# def read_record(conf, record_id):
#     repo_dir = get_repo_dir()
#     if repo_dir is None:
#         raise ManagedException("No git repo found")

#     if conf['record_dir'] is None:
#         raise ManagedException("Must specify record_dir in conf")
#     record_dir_path = join(repo_dir, conf['record_dir'])
    
#     filename = record_id
#     file_path = join(record_dir_path, filename)
#     with open(file_path, 'r') as f:
#         return f.read()

def read_branch_record(conf, treeish, record_id):
    if conf['record_dir'] is None:
        raise ManagedException("Must specify record_dir in conf")
    git_path = join(conf['record_dir'], record_id)
    return show_file(treeish, git_path)