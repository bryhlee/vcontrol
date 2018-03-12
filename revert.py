import os
import sys
import shutil
import json
import filecmp

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

def retrieve_file_paths(starting_directory):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(starting_directory, topdown=True):
        dirnames[:] = [d for d in dirnames if d != '.vcs']
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths

def revert_command(args):
    commit_tag = args.commit_tag

    if not os.path.exists(VCS_PATH):
        print("Repository has not been intialized, or isn't detected. Run 'vcontrol create [username]'")
        sys.exit(1)

    config = read_config_file()
    username = config['user']

    REVERT_PATH = "{}/commits/{}".format(VCS_PATH, commit_tag)
    VCS_FILE_PATH = "{}/.vcs".format(REVERT_PATH)
    vcs_dict = read_json_file(VCS_FILE_PATH)

    file_paths = retrieve_file_paths(REVERT_PATH)
    for file in file_paths:
        



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
