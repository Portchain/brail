#!/usr/bin/env python3
import sys
import json
import os
import binascii
from os.path import expanduser, join
from git import get_repo_dir, add_file, list_tree, show_file
from editor import call_editor
from diff import get_diff
from conf import get_conf_paths, parse_conf_file, merge_confs

class ManagedException(Exception):
    pass

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

# Returns buffer
def read_record(conf, record_id):
    repo_dir = get_repo_dir()
    if repo_dir is None:
        raise ManagedException("No git repo found")

    if conf['record_dir'] is None:
        raise ManagedException("Must specify record_dir in conf")
    record_dir_path = join(repo_dir, conf['record_dir'])
    
    filename = record_id
    file_path = join(record_dir_path, filename)
    with open(file_path, 'r') as f:
        return f.read()

def read_branch_record(conf, treeish, record_id):
    if conf['record_dir'] is None:
        raise ManagedException("Must specify record_dir in conf")
    git_path = join(conf['record_dir'], record_id)
    return show_file(treeish, git_path)

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
    elif args[0] == 'diff':
        if len(args) == 1:
            base_treeish = conf['default_comparison_base']
            comparison_treeish = 'HEAD'
        elif len(args) == 2:
            base_treeish = args[1]
            comparison_treeish = 'HEAD'
        elif len(args) >= 3:
            base_treeish = args[2]
            comparison_treeish = args[1]
        added_records, removed_records = get_diff(comparison_treeish, base_treeish, conf)
        for record_id in added_records:
            lines = read_record(conf, record_id).splitlines()
            print('+ ' + lines[0])
            for line in lines[1:]:
                print('+     ' + line)
        for record_id in removed_records:
            lines = read_branch_record(conf, base_treeish, record_id).splitlines()
            print('- ' + lines[0])
            for line in lines[1:]:
                print('-     ' + line)
    else:
        error_output('Unknown command: {0}'.format(args[0]))

if __name__ == "__main__":
    main(sys.argv[1:])