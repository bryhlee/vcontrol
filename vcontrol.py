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

    parser_commit = subparsers.add_parser('commit', help='Commits changes in the current repository.')
    parser_commit.set_defaults(func=commit_command)

    parser_fetch = subparsers.add_parser('fetch', help='Fetches commits from a specified repository.')

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

def get_file_paths(starting_directory):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(starting_directory, topdown=True):
        dirnames[:] = [d for d in dirnames if d != '.vcs']
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths

def get_unchanged_deleted_files(commit_user, last_commit_value, working_files):
    unchanged_files = []
    deleted_files = []
    if last_commit_value == 0:
        return unchanged_files, deleted_files

    LAST_COMMIT_SUBDIR = VCS_PATH + '/commits/V{:05d}_{}'.format(last_commit_value, commit_user)

    vcs = read_json_file('{}/.vcs'.format(LAST_COMMIT_SUBDIR))

    for file in vcs['commits']:
        if file in working_files:
            if filecmp.cmp(file, vcs['commits'][file]['subdir'] + file[1:]):
                unchanged_files.append(file)
        else:
            deleted_files.append(file)
    return unchanged_files, deleted_files

def create_commit_subdir(working_files, unchanged_files, deleted_files, last_commit_user, last_commit_value, new_commit_user, new_commit_value):
    print('commit:')

    NEW_COMMIT_SUBDIR = VCS_PATH + '/commits/V{:05d}_{}'.format(new_commit_value, new_commit_user)

    def custom_ignore(path, filenames):
        ignore = []
        for filename in filenames:
            if os.path.join(path, filename) in unchanged_files:
                ignore.append(filename)
            elif filename == '.vcs':
                ignore.append(filename)
        return ignore

    shutil.copytree(src=WORKING_DIR,
                    dst=NEW_COMMIT_SUBDIR,
                    ignore=custom_ignore)

    if last_commit_value == 0:
        vcs = {'commits': {}, 'latest_fetch': {}}
    else:
        last_vcs_filepath = VCS_PATH + '/commits/V{:05d}_{}/.vcs'.format(last_commit_value, last_commit_user)
        vcs = read_json_file(last_vcs_filepath)
        for deleted_file in deleted_files:
            print('  - deletion: {}'.format(deleted_file))
            vcs['commits'].pop(deleted_file)
    for file_path in [fp for fp in working_files if fp not in unchanged_files]:
        if file_path not in vcs['commits']:
            print('  + addition: {}'.format(file_path))
        else:
            print('  ~ change: {}'.format(file_path))
        vcs['commits'][file_path] = {
            'value': new_commit_value,
            'subdir': NEW_COMMIT_SUBDIR,
            'user': new_commit_user
        }
    write_json_file(NEW_COMMIT_SUBDIR + '/.vcs', vcs)


def commit_command(args):
    if not os.path.exists(VCS_PATH):
        print("Repository has not been intialized, or isn't detected. Run 'vcontrol create [username]'")
        sys.exit(1)

    config = read_config_file()
    working_files = get_file_paths('.')

    if not working_files:
        print("No files exist to be commited.")
        sys.exit(1)

    last_commit_value = config['last_commit']['value']
    new_commit_value = last_commit_value + 1

    print('Creating new commit V{:05d} --> V{:05d}'.format(last_commit_value, new_commit_value))

    unchanged_files, deleted_files = get_unchanged_deleted_files(
        commit_user=config['last_commit']['user'],
        last_commit_value=last_commit_value,
        working_files=working_files
    )

    if unchanged_files == working_files and not deleted_files:
        print("No files have been changed and therefore there is nothing to commit.")
        sys.exit(1)
    
    create_commit_subdir(
        working_files=working_files,
        unchanged_files=unchanged_files,
        deleted_files=deleted_files,
        last_commit_user=config['last_commit']['user'],
        last_commit_value=last_commit_value,
        new_commit_user=config['user'],
        new_commit_value=new_commit_value
    )

    config['last_commit']['value'] = new_commit_value
    config['last_commit']['user'] = config['user']
    update_config_file(config)


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
