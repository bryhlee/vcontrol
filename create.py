import os
import sys
import errno
import json
import argparse

# function to write a dict to json file
def write_json(data, filePointer):
    json.dump(data, filePointer)

# function to read a dict from json file
def read_json(filePointer):
    json = json.load(filePointer)
    return json

# main function 
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

    parser_fetch = subparsers.add_parser('fetch', help='Fetches commits from a specified repository.')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)

def create_command(args):
    username = args.username

    print("Creating repository for {}".format(username))

    VCS_PATH = "./.vcs"

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

    CONFIG_PATH = "{}/config.json".format(VCS_PATH)

    # create userdict to store to config.json
    with open(CONFIG_PATH, 'w') as config_file:
        userdict = {
            'user': username,
            'last-fetch': "NULL"
        }
        write_json(userdict, config_file)


if __name__ == "__main__":
    main()
