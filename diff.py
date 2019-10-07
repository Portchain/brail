from git import list_tree

def get_diff(comparison_treeish, base_treeish, conf):
    record_dir = conf['record_dir']
    comparison_record_ids = set(list_tree(comparison_treeish, record_dir + '/'))
    base_record_ids = set(list_tree(base_treeish, record_dir + '/'))
    added_records = comparison_record_ids - base_record_ids
    removed_records = base_record_ids - comparison_record_ids
    return list(added_records), list(removed_records)