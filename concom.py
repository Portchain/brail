#!/usr/bin/env python3
import sys
import json
from git import add_file
from editor import call_editor
from diff import get_diff
from conf import get_conf_paths, parse_conf_file, merge_confs
from output import output, error_output
from errors import ManagedException
from records import create_record, read_branch_record

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
                output('+ ' + lines[0])
            for line in lines[1:]:
                output('+     ' + line)
        removed_records = [
            {'id': record_id, 'content': read_branch_record(conf, base_treeish, record_id)}
            for record_id in removed_record_ids
        ]
        # Sort by record content alphabetically
        removed_records.sort(key=lambda r: r['content'])
        for record in removed_records:
            lines = record['content'].splitlines()
            if lines > 0:
                output('- ' + lines[0])
            for line in lines[1:]:
                output('-     ' + line)
    else:
        raise ManagedException('Unknown command: {0}'.format(args[0]))

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except ManagedException as e:
        error_output(str(e))
