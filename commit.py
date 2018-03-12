import os
import sys
import shutil
import json
import filecmp

WORKING_DIR = "."
VCS_PATH = WORKING_DIR + "/.vcs"
CONFIG_PATH = VCS_PATH + "/config.json"

def write_json(data, filePointer):
    json.dump(data, filePointer, indent=4,)

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4,)

def read_json(filePointer):
    data = json.load(filePointer)
    return data

def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data

def read_config_file():
    return read_json_file(CONFIG_PATH)

def update_config_file(config_dict):
    write_json_file(CONFIG_PATH, config_dict)

def retrieve_file_paths(starting_directory):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(starting_directory, topdown=True):
        dirnames[:] = [d for d in dirnames if d != '.vcs']
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths

def determine_unchanged_files(commit_user, last_commit_value, working_files):
    unchanged_files = []
    if last_commit_value == 0:
        return unchanged_files

    LAST_COMMIT_SUBDIR = VCS_PATH + '/commits/V{:05d}_{}'.format(last_commit_value, commit_user)

    vcs = read_json_file('{}/.vcs'.format(LAST_COMMIT_SUBDIR))

    for file in working_files:
        if file in vcs['commits']:
            if filecmp.cmp(file, vcs['commits'][file]['subdir'] + file[1:]):
                unchanged_files.append(file)

    return unchanged_files

def create_vcs_file(unchanged_files, last_commit_user, new_commit_user, new_commit_value, last_commit_value, new_commit_dir, file_paths):
    new_vcs_filepath = new_commit_dir + '/.vcs'

    if last_commit_value == 0:
        vcs = {
            'commits': {},
            'latest_fetch': {}
        }
    else:
        last_vcs_filepath = VCS_PATH + '/commits/V{:05d}_{}/.vcs'.format(last_commit_value, last_commit_user)
        vcs = read_json_file(last_vcs_filepath)
    for file_path in [fp for fp in file_paths if fp not in unchanged_files]:
        vcs['commits'][file_path] = {
            'value': new_commit_value,
            'subdir': new_commit_dir,
            'user': new_commit_user
        }
    write_json_file(new_vcs_filepath, vcs)


def main():
    if not os.path.exists(VCS_PATH):
        print("Repository has not been intialized, or isn't detected. Run 'vcontrol create [username]'")
        sys.exit(1)

    config = read_config_file()
    working_files = retrieve_file_paths('.')

    if not working_files:
        print("No files exist to be commited.")
        sys.exit(1)

    last_commit_value = config['last_commit']['value']
    new_commit_value = last_commit_value + 1

    NEW_COMMIT_SUBDIR = VCS_PATH + '/commits/V{:05d}_{}'.format(new_commit_value, config['user'])

    unchanged_files = determine_unchanged_files(config['last_commit']['user'], last_commit_value, working_files)

    if unchanged_files == working_files:
        print("No files have been changed and therefore there is nothing to commit.")
        sys.exit(1)

    def custom_ignore(path, filenames):
        ignore = []
        for filename in filenames:
            if os.path.join(path, filename) in unchanged_files:
                ignore.append(filename)
            elif filename == '.vcs':
                ignore.append(filename)
            elif filename == '.git':
                ignore.append(filename)
        return ignore

    shutil.copytree(src=WORKING_DIR,
                    dst=NEW_COMMIT_SUBDIR,
                    ignore=custom_ignore)
    
    create_vcs_file(unchanged_files, config['last_commit']['user'], config['user'], new_commit_value, last_commit_value, NEW_COMMIT_SUBDIR, working_files)

    config['last_commit']['value'] = new_commit_value
    config['last_commit']['user'] = config['user']
    update_config_file(config)
        

if __name__ == "__main__":
    main()