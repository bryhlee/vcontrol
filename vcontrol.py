import os
import sys
import errno
import json
import shutil
import filecmp
import argparse


WORKING_DIR = "."
VCS_PATH = WORKING_DIR + "/.vcs"
CONFIG_PATH = VCS_PATH + "/config.json"


def main():
    parser = argparse.ArgumentParser(
        prog='vcontrol',
        description='vcontrol is a demo version control system for COEN 317, Distributed Computing.'
    )
    subparsers = parser.add_subparsers(title='command list', metavar='action')

    parser_create = subparsers.add_parser('create', help='Initializes a new vcontrol repository as the current directory.')
    parser_create.add_argument('username', type=str, help='Specified username for the vcontrol repo.')
    parser_create.set_defaults(func=create_command)

    parser_info = subparsers.add_parser('info', help='Shows information regarding the status of the current repository.')
    parser_info.set_defaults(func=info_command)

    parser_commit = subparsers.add_parser('commit', help='Commits changes in the current repository.')
    parser_commit.add_argument('-i', '--ignore', dest='ignore', nargs='*', help='Ignores file(s) for commit.', default=[])
    parser_commit.set_defaults(func=commit_command)

    parser_fetch = subparsers.add_parser('fetch', help='Fetches commits from a specified repository.')

    parser_revert = subparsers.add_parser('revert', help='Reverts the working directory back to a previous commit stage.')
    parser_revert.add_argument('commit_tag', type=str, help='Specified vcontrol commit to revert the project to.')
    parser_revert.set_defaults(func=revert_command)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)


def write_json(data, filePointer):
    json.dump(data, filePointer)


def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4,)


def read_json(filePointer):
    json = json.load(filePointer)
    return json


def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data


def read_config_file():
    return read_json_file(CONFIG_PATH)


def update_config_file(config_dict):
    write_json_file(CONFIG_PATH, config_dict)


def get_file_paths(starting_directory, to_ignore):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(starting_directory, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in to_ignore]
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths


def get_unchanged_deleted_files(working_files, config):
    unchanged_files = []
    deleted_files = []
    if config['last_commit']['value'] == 0:
        return unchanged_files, deleted_files

    LAST_COMMIT_SUBDIR = VCS_PATH + '/commits/V{:05d}_{}'.format(config['last_commit']['value'],
                                                                 config['last_commit']['user'])

    vcs = read_json_file('{}/.vcs'.format(LAST_COMMIT_SUBDIR))

    for file in vcs['commits']:
        if file in working_files:
            if filecmp.cmp(file, vcs['commits'][file]['subdir'] + file[1:]):
                unchanged_files.append(file)
        else:
            deleted_files.append(file)
    return unchanged_files, deleted_files


def create_commit_subdir(working_files, unchanged_files, deleted_files, to_ignore, config):
    new_commit_value = config['last_commit']['value'] + 1
    NEW_COMMIT_SUBDIR = VCS_PATH + '/commits/V{:05d}_{}'.format(new_commit_value, config['last_commit']['user'])

    def custom_ignore(path, filenames):
        ignore = []
        for filename in filenames:
            if os.path.join(path, filename) in unchanged_files:
                ignore.append(filename)
            elif filename in to_ignore:
                ignore.append(filename)
        return ignore

    shutil.copytree(src=WORKING_DIR,
                    dst=NEW_COMMIT_SUBDIR,
                    ignore=custom_ignore)

    if config['last_commit']['value'] == 0:
        vcs = {'commits': {}, 'latest_fetch': {}}
    else:
        last_vcs_filepath = VCS_PATH + '/commits/V{:05d}_{}/.vcs'.format(config['last_commit']['value'],
                                                                         config['last_commit']['user'])
        vcs = read_json_file(last_vcs_filepath)
        for deleted_file in deleted_files:
            vcs['commits'].pop(deleted_file)
    for file_path in [fp for fp in working_files if fp not in unchanged_files]:
        vcs['commits'][file_path] = {
            'value': new_commit_value,
            'subdir': NEW_COMMIT_SUBDIR,
            'user': config['user']
        }
    write_json_file(NEW_COMMIT_SUBDIR + '/.vcs', vcs)


def clear_working_directory():
    for file in os.listdir(WORKING_DIR):
        if file == '.':
            continue
        elif file == '..':
            continue
        elif file == '.vcs':
            continue
        else:
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)


def print_file_status(working_files, unchanged_files, deleted_files, config, primer=None):
    if primer is not None:
        print('{}:'.format(primer))
    if config['last_commit']['value'] == 0:
        for file in working_files:
            print('  {}+{} addition: {}'.format('\033[92m', '\033[0m', file))
    else:
        last_vcs_filepath = VCS_PATH + '/commits/V{:05d}_{}/.vcs'.format(config['last_commit']['value'],
                                                                         config['last_commit']['user'])
        vcs = read_json_file(last_vcs_filepath)
        for deleted_file in deleted_files:
            print('  {}-{} deletion: {}'.format('\033[91m', '\033[0m', deleted_file))
        for file_path in [fp for fp in working_files if fp not in unchanged_files]:
            if file_path not in vcs['commits']:
                print('  {}+{} addition: {}'.format('\033[92m', '\033[0m', file_path))
            else:
                print('  {}~{} change: {}'.format('\033[93m', '\033[0m', file_path))


def info_command(args):
    if not os.path.exists(VCS_PATH):
        print("Repository has not been intialized, or isn't detected. Run 'vcontrol create [username]'")
        sys.exit(1)

    working_files = get_file_paths('.', ['.vcs'])
    config = read_config_file()
    last_commit_tag = 'V{:05d}_{}'.format(config['last_commit']['value'], config['last_commit']['user'])
    print('On commit tag {}'.format(last_commit_tag))

    unchanged_files, deleted_files = get_unchanged_deleted_files(working_files, config)
    if unchanged_files == working_files and not deleted_files:
        print("Working directory is clean - no changes.")
    else:
        print_file_status(working_files, unchanged_files, deleted_files, config, 'info')

def revert_command(args):
    if not os.path.exists(VCS_PATH):
        print("Repository has not been intialized, or isn't detected. Run 'vcontrol create [username]'")
        sys.exit(1)

    confirm = input('Revert to commit {}? You will lose uncommited changes in your working directory. (y/N)'.format(args.commit_tag))
    if confirm != 'y':
        if confirm != 'N':
            print('Invalid input...')
        print('Canceling revert.')
        sys.exit(1)

    print('revert:')

    config = read_config_file()

    clear_working_directory()

    REVERT_PATH = "{}/commits/{}".format(VCS_PATH, args.commit_tag)
    VCS_FILE_PATH = "{}/.vcs".format(REVERT_PATH)
    vcs = read_json_file(VCS_FILE_PATH)

    file_paths = list(vcs['commits'])
    for file in file_paths:
        print('  {}->{} revert: {} | {}'.format('\033[93m', '\033[0m', file, os.path.basename(vcs['commits'][file]['subdir'])))
        src_path = os.path.join(vcs['commits'][file]['subdir'], file)
        os.makedirs(os.path.dirname(file), exist_ok=True)
        shutil.copy(src_path, file)


def commit_command(args):
    if not os.path.exists(VCS_PATH):
        print("Repository has not been intialized, or isn't detected. Run 'vcontrol create [username]'")
        sys.exit(1)

    args.ignore.append('.vcs')
    working_files = get_file_paths('.', args.ignore)

    if not working_files:
        print("No files exist to be commited.")
        sys.exit(1)

    config = read_config_file()

    new_commit_value = config['last_commit']['value'] + 1
    last_commit_tag = 'V{:05d}_{}'.format(config['last_commit']['value'], config['last_commit']['user'])
    new_commit_tag = 'V{:05d}_{}'.format(new_commit_value, config['user'])

    print('Creating new commit {} --> {}'.format(last_commit_tag, new_commit_tag))

    unchanged_files, deleted_files = get_unchanged_deleted_files(working_files, config)

    if unchanged_files == working_files and not deleted_files:
        print("No files have been changed and therefore there is nothing to commit.")
        sys.exit(1)

    print_file_status(working_files, unchanged_files, deleted_files, config, 'commit')

    create_commit_subdir(
        working_files=working_files,
        unchanged_files=unchanged_files,
        deleted_files=deleted_files,
        to_ignore=args.ignore,
        config=config
    )

    config['last_commit']['value'] = new_commit_value
    config['last_commit']['user'] = config['user']
    update_config_file(config)
    print('Changes successfully commited, on tag {}'.format(new_commit_tag))


def create_command(args):
    username = args.username

    print("Creating repository for {}".format(username))

    # check if .vcs folder already exists
    if os.path.exists(VCS_PATH):
        print ("Repository already created")
        return

    # create the .vcs folder
    try:
        os.makedirs(VCS_PATH)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # create commits folder
    COMMITS_PATH = "{}/commits".format(VCS_PATH)
    try:
        os.makedirs(COMMITS_PATH)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    CONFIG_PATH = "{}/config.json".format(VCS_PATH)

    userdict = {
        'user': username,
        'last_fetch': "NULL",
        'last_commit': {
            'user': username,
            'value': 0
        }
    }
    update_config_file(userdict)

if __name__ == "__main__":
    main()
