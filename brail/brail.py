#!/usr/bin/env python3
import sys
import json
import argparse

from .git import add_file
from .editor import call_editor
from .diff import get_diff
from .conf import get_conf_paths, parse_conf_file, merge_confs
from .output import output, error_output
from .errors import ManagedException
from .records import create_record, read_branch_record, get_record_dir_path, get_record_path, list_workdir_records, delete_record
from .usage import usage_string

RECORD_TYPES = ('feat', 'fix', 'manual')

create_record_parser = argparse.ArgumentParser()
create_record_parser.add_argument('record_type', choices=RECORD_TYPES)
create_record_parser.add_argument('-m', '--message')

diff_parser = argparse.ArgumentParser()
diff_parser.add_argument('-v', '--verbose', action='store_true')
diff_parser.add_argument('treeishes', nargs='*')

def run_brail(args):
    conf_paths = get_conf_paths()
    confs = [parse_conf_file(path) for path in conf_paths]
    conf = merge_confs(confs)
    if not args:
        output(usage_string)
    elif args[0] in ('conf', 'config'):
        if len(args) > 1:
            raise ManagedException('Unexpected additional arguments: {0}'.format(args[1:]))
        output(json.dumps(conf, indent=4))
    elif args[0] in ('edit'):
        if len(args) < 2:
            raise ManagedException('Must provide id or partial id')
        elif len(args) > 2:
            raise ManagedException('Unexpected additional arguments: {0}'.format(args[2:]))
        else:
            partial_record_id = args[1]
            record_ids = list_workdir_records(conf, partial_record_id)
            if not record_ids:
                raise ManagedException('No record in workdir matches: {0}'.format(partial_record_id))
            elif len(record_ids)>1:
                raise ManagedException('Ambigious pattern. Multiple records match')
            else:
                record_id = record_ids[0]
                record_path = get_record_path(conf, record_id)
                if conf['editor'] is not None:
                    call_editor(conf['editor'], record_path)
                else:
                    raise ManagedException('No editor specified')
    elif args[0] in ('delete'):
        if len(args) < 2:
            raise ManagedException('Must provide id or partial id')
        elif len(args) > 2:
            raise ManagedException('Unexpected additional arguments: {0}'.format(args[2:]))
        else:
            partial_record_id = args[1]
            record_ids = list_workdir_records(conf, partial_record_id)
            if not record_ids:
                raise ManagedException('No record in workdir matches: {0}'.format(partial_record_id))
            elif len(record_ids)>1:
                raise ManagedException('Ambiguous pattern. Multiple records match')
            else:
                record_id = record_ids[0]
                record_dir_path = get_record_dir_path(conf)
                delete_record(record_dir_path, record_id)
    elif args[0] in RECORD_TYPES:
        parsed_args = create_record_parser.parse_args(args)
        record_fields = {"type": parsed_args.record_type}
        if parsed_args.message:
            record_fields["description"] = parsed_args.message
            record_id, record_path = create_record(conf, record_fields)
        elif conf['editor'] is not None:
            record_id, record_path = create_record(conf, record_fields)
            call_editor(conf['editor'], record_path)
        else:
            output('No editor specified! Record at {0}'.format(record_path))
        output(record_id)
        if conf['auto_add']:
            add_file(record_path)
    elif args[0] == 'diff':
        parsed_args = diff_parser.parse_args(args[1:])
        treeishes = parsed_args.treeishes
        if len(treeishes) == 0:
            base_treeish = conf['default_comparison_base']
            comparison_treeish = 'HEAD'
        elif len(treeishes) == 1:
            base_treeish = treeishes[0]
            comparison_treeish = 'HEAD'
        elif len(treeishes) == 2:
            base_treeish = treeishes[1]
            comparison_treeish = treeishes[0]
        elif len(treeishes) > 2:
            raise ManagedException('Unexpected additional arguments: {0}'.format(treeishes[2:]))
        added_record_ids, removed_record_ids = get_diff(conf, comparison_treeish, base_treeish)
        output('Changes in {0} compared to {1}:'.format(comparison_treeish, base_treeish))
        added_records = [
            {'id': record_id, 'content': read_branch_record(conf, comparison_treeish, record_id)}
            for record_id in added_record_ids
        ]
        # Sort by record content alphabetically
        added_records.sort(key=lambda r: r['content'])
        for record in added_records:
            lines = record['content'].splitlines()
            if lines:
                if parsed_args.verbose:
                    output('+ ID: ' + record['id'])
                output('+ ' + lines[0])
            for line in lines[1:]:
                output('+     ' + line)
            if len(lines) > 1 and lines[-1] != '':
                output('+')
        removed_records = [
            {'id': record_id, 'content': read_branch_record(conf, base_treeish, record_id)}
            for record_id in removed_record_ids
        ]
        # Sort by record content alphabetically
        removed_records.sort(key=lambda r: r['content'])
        for record in removed_records:
            lines = record['content'].splitlines()
            if lines:
                if parsed_args.verbose:
                    output('- ID: ' + record['id'])
                output('- ' + lines[0])
            for line in lines[1:]:
                output('-     ' + line)
            if len(lines) > 1 and lines[-1] != '':
                output('-')
    else:
        raise ManagedException('Unknown command: {0}'.format(args[0]))

def main():
    try:
        run_brail(sys.argv[1:])
    except ManagedException as e:
        error_output(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()