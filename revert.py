import os
import sys
import shutil
import json
import filecmp
import argparse

WORKING_DIR = "."
VCS_PATH = WORKING_DIR + "/.vcs"
CONFIG_PATH = VCS_PATH + "/config.json"

def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4,)

def read_config_file():
    return read_json_file(CONFIG_PATH)

def update_config_file(config_dict):
    write_json_file(CONFIG_PATH, config_dict)

def clear_working_directory():
    for file in os.listdir(WORKING_DIR):
        if file == ".":
            continue
        elif file == "..":
            continue
        elif file == ".git":
            continue
        elif file == ".vcs":
            continue
        else:
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)

def revert_command(args):
    commit_tag = args.commit_tag

    if not os.path.exists(VCS_PATH):
        print("Repository has not been intialized, or isn't detected. Run 'vcontrol create [username]'")
        sys.exit(1)

    config = read_config_file()

    clear_working_directory()

    REVERT_PATH = "{}/commits/{}".format(VCS_PATH, commit_tag)
    VCS_FILE_PATH = "{}/.vcs".format(REVERT_PATH)
    vcs = read_json_file(VCS_FILE_PATH)

    file_paths = list(vcs['commits'])
    for file in file_paths:
        src_path = os.path.join(vcs['commits'][file]['subdir'], file)
        os.makedirs(os.path.dirname(file), exist_ok=True)
        shutil.copy(src_path, file)

def main():

    parser = argparse.ArgumentParser(
        prog='vcontrol',
        description='vcontrol is a demo version control system for COEN 317, Distributed Computing.'
    )
    subparsers = parser.add_subparsers(title='command list', metavar='action')

    parser_revert = subparsers.add_parser('revert', help='Reverts the working directory back to a previous commit stage.')
    parser_revert.add_argument('commit_tag', type=str, help='Specified vcontrol commit to revert the project to.')
    parser_revert.set_defaults(func=revert_command)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
