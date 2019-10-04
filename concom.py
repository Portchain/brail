#!/usr/bin/env python3
import sys
import json
import os
import binascii
from os.path import expanduser, join
from git import get_repo_dir, add_file
from editor import call_editor

class ManagedException(Exception):
    pass

def merge_confs(confs):
    merged_conf = get_default_conf()
    for conf in confs:
        merged_conf = {**merged_conf, **conf}
    return merged_conf

def parse_conf_file(path):
    return json.loads(open(path).read())

def get_default_conf():
    return {
        "record_dir": None,
        "editor": None,
        "auto_add": True,
    }

def get_conf_paths():
    paths = []
    
    repo_dir = get_repo_dir()
    if repo_dir is not None:
        repo_conf_path = join(get_repo_dir(), '.concomconf')
        if os.path.exists(repo_conf_path):
            paths.append(repo_conf_path)

    home_conf_path = join(expanduser("~"), '.concomconf')
    if os.path.exists(home_conf_path):
        paths.append(home_conf_path)
    
    return paths

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
    record_dir = join(repo_dir, conf['record_dir'])
    if conf['record_dir'] is not None:
        record_id = generate_record_id()
        if record_fields is not None:
            record_buffer = record_fields.get('type', 'type') + ': ' + record_fields.get('description', '')
        else:
            record_buffer = None
        record_path = write_record(record_dir, record_id, record_buffer)
        return record_id, record_path
    else:
        raise ManagedException("Must specify record_dir in conf")

def error_output(*x):
    print(*x, file=sys.stderr)

def output(*x):
    print(*x)

def main(args):
    conf_paths = get_conf_paths()
    confs = [parse_conf_file(path) for path in conf_paths]
    conf = merge_confs(confs)
    if args[0] == 'conf':
        output(json.dumps(conf, indent=4))
    elif args[0] == 'blank':
        record_id, record_path = create_record(conf, None)
        output(record_id)
    elif args[0] in ('feat', 'fix', 'manual'):
        record_fields = {"type": args[0]}
        if len(args) >= 3 and args[1] == '-m':
            record_fields["description"] = args[2]
        record_id, record_path = create_record(conf, record_fields)
        if conf['editor'] is not None:
            call_editor(conf['editor'], record_path)
        output(record_id)
        if conf['auto_add']:
            add_file(record_path)
    else:
        error_output('Unknown command: {0}'.format(args[0]))

if __name__ == "__main__":
    main(sys.argv[1:])