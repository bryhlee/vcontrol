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
    data = json.load(filePointer)
    return data

def main():

    print("Checking repository")
    CWD_PATH = "."
    VCS_PATH = "./.vcs"

    # check for .vcs folder
    if not os.path.exists(VCS_PATH):
        print ("No repository")
        return

    CONFIG_PATH = "./.vcs/config.json"
    with open(CONFIG_PATH, "r") as config_file:
        userdict = read_json(config_file)
        commit = userdict['last-commit']
        username = userdict['user']
    # get list of files
    # for file in os.listdir(VCS_PATH):
    #     print(os.path.join(VCS_PATH, file))

    # provision commit_path
    if commit == 0:
        COMMIT_PATH = "V0"
    else:
        COMMIT_PATH = "./.vcs/commits/V%05d_%s" %commit, username
    print(COMMIT_PATH)

    filelist = []
    check_files(CWD_PATH, filelist, COMMIT_PATH)
    print (filelist)

def trim_path(filepath, prefix):
    if filepath.startswith(prefix):
        return filepath[len(prefix):]
    else:
        return filepath

def check_files(dirpath, filelist, commitpath):

    if not os.path.exists(dirpath):
        return

    for file in os.listdir(dirpath):
        filepath = os.path.join(dirpath, file)

        # ignore ., .., and repo files
        if filepath == "./.git":
            continue
        if filepath == "./.":
            continue
        if filepath == "./..":
            continue
        if filepath == "./.vcs":
            continue

        # if we have no commits, all files are new
        if commitpath == "V0":
            filelist.append(filepath)

        if os.path.isdir(filepath):
            listfiles(filepath, filelist)


if __name__ == "__main__":
    main()
