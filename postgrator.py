from git import list_tree
import re

postgator_fwd_migration_regex = re.compile('^([0-9]+)\.do.*\.sql$')

def list_postgrator_records(conf, treeish):
    if conf['postgrator_dir'] is None:
        return []
    postgrator_dir = conf['postgrator_dir']
    return ['pg/' + x for x in list_tree(treeish, postgrator_dir + '/') if postgator_fwd_migration_regex.match(x) is not None]