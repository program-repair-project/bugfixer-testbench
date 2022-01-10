#!/usr/bin/env python3

# ./line-matching.py [path to version n] [path to version n+1]

import codecs
import filecmp
import json
import os
import subprocess
import sys

old_dir = sys.argv[1] if not sys.argv[1].endswith('/') else sys.argv[1][:-1]
new_dir = sys.argv[2] if not sys.argv[2].endswith('/') else sys.argv[2][:-1]


def get_filepaths(directory):
    file_paths = set()
    for root, directories, files in os.walk(directory):
        for filename in [
                f for f in files
                if (f.endswith('.c') or f.endswith('.h')) and (
                    not os.path.islink(os.path.join(root, f)))
        ]:
            filepath = os.path.join(root, filename)[len(directory) + 1:]
            file_paths.add(filepath)
    return file_paths


def line_match(file1, file2):
    info = []
    added_lines = set()
    p = subprocess.Popen(['diff', file1, file2], stdout=subprocess.PIPE)
    result = p.stdout.read().decode('UTF-8', 'ignore').strip().split('\n')
    num_added_lines = 0
    num_deleted_lines = 0
    num_changed_lines = 0
    for line in [
            line for line in result if not line.startswith('-')
            and not line.startswith('<') and not line.startswith('>')
    ]:
        diff_type = (set(line) & set(['a', 'd', 'c'])).pop()
        diffs = line.split(diff_type)
        old_lines = diffs[0].split(',')
        new_lines = diffs[1].split(',')
        old_from = int(old_lines[0])
        old_to = int(old_lines[1]) if len(old_lines) > 1 else int(old_lines[0])
        new_from = int(new_lines[0])
        new_to = int(new_lines[1]) if len(new_lines) > 1 else int(new_lines[0])
        old_length = old_to - old_from + 1
        new_length = new_to - new_from + 1

        # lines added
        if diff_type == 'a':
            info.append((new_to + 1, -1 * new_length))
            added_lines.update(range(new_from, new_to + 1))
            num_added_lines += new_length
        # lines deleted
        elif diff_type == 'd':
            info.append((new_to + 1, old_length))
            num_deleted_lines += old_length
        # lines changed
        elif diff_type == 'c' and old_length != new_length:
            info.append((new_to, old_length - new_length))
            num_changed_lines += new_length
        elif diff_type == 'c':
            num_changed_lines += old_length

    if len(added_lines) == 0 and num_changed_lines == 0 and info == []:
        return (0, 0, 0, [])

    num_lines = sum(
        1
        for line in codecs.open(file2, 'r', encoding='utf-8', errors='ignore'))
    matching = []
    diff = 0
    for i in range(1, num_lines + 1):
        if i in added_lines:
            matching.append(0)
        elif info != [] and i == info[0][0]:
            diff = diff + info[0][1]
            info = info[1:]
            matching.append(i + diff)
        else:
            matching.append(i + diff)
    return (num_added_lines, num_deleted_lines, num_changed_lines, matching)


old_files = get_filepaths(old_dir)
new_files = get_filepaths(new_dir)

added_files = new_files - old_files
deleted_files = old_files - new_files
common_files = new_files - added_files

print("Added files")
total_added_lines = 0
for f in [f for f in added_files if 'test' not in f and 'gnulib' not in f]:
    f = new_dir + '/' + f
    num_lines = sum(
        1 for line in codecs.open(f, 'r', encoding='utf-8', errors='ignore'))
    total_added_lines += num_lines
    print("  {}: {}".format(f, num_lines))
print("Total # added lines: {}".format(total_added_lines))

print("Deleted files")
total_deleted_lines = 0
for f in [f for f in deleted_files if 'test' not in f and 'gnulib' not in f]:
    f = old_dir + '/' + f
    num_lines = sum(
        1 for line in codecs.open(f, 'r', encoding='utf-8', errors='ignore'))
    total_deleted_lines += num_lines
    print("  {}: {}".format(f, num_lines))
print("Total # deleted lines: {}".format(total_deleted_lines))

print("Common files")
report = {}
report['added_files'] = [os.path.basename(f) for f in list(added_files)]
report['changed_files'] = {}
report['unchanged_files'] = []
total_changed_lines = 0
total_unchanged_lines = 0
total_lines = 0
for f in common_files:
    old_file = old_dir + '/' + f
    new_file = new_dir + '/' + f
    num_lines = sum(1 for line in codecs.open(
        new_file, 'r', encoding='utf-8', errors='ignore'))
    total_lines += num_lines
    if not filecmp.cmp(old_file, new_file, shallow=False):
        (added_lines, deleted_lines, changed_lines,
         matching) = line_match(old_file, new_file)
        total_added_lines += added_lines
        total_deleted_lines += deleted_lines
        total_changed_lines += changed_lines
        unchanged_lines = num_lines - added_lines - changed_lines
        total_unchanged_lines += unchanged_lines
        print("  {}: {} total, {} added, {} deleted, {} changed, {} unchanged".
              format(f, num_lines, added_lines, deleted_lines, changed_lines,
                     unchanged_lines))
        if matching != []:
            basename = os.path.basename(f)
            report['changed_files'][basename] = matching
    else:
        basename = os.path.basename(f)
        report['unchanged_files'].append(basename)
        total_unchanged_lines += num_lines
        print("  {}: {} total, {} unchanged".format(f, num_lines, num_lines))

with open('line_matching.json', 'w') as f:
    json.dump(report, f, indent=2)

print("Total # added lines in common files: {}".format(total_added_lines))
print("Total # deleted lines in common files: {}".format(total_deleted_lines))
print("Total # changed lines in common files: {}".format(total_changed_lines))
print("Total # changed lines: {}".format(total_added_lines +
                                         total_changed_lines))
print("Total # unchanged lines: {}".format(total_unchanged_lines))
print("Total # lines: {}".format(total_lines))
