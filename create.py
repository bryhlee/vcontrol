import argparse
import os
import errno
import json

# function to write a dict to json file
def writejson( data, filePointer ):
    json.dump(data, filePointer)

# function to read a dict from json file
def readjson( filePointer ):
    dict = json.load(filePointer)
    return dict

# main function 
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("create")
    parser.add_argument("username", type=str)
    args = parser.parse_args()
    username = args.username

    print ("creating repository for " + username)

    vcs_path = "./.vcs"

    # check if .vcs folder already exists
    if os.path.exists(vcs_path):
        print ("repository already created")
        return

    # create the .vcs folder
    try:
        os.makedirs(vcs_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # create user dict
    # dict_path = vcs_path + "/config.py"
    # dictFile = open(dict_path, "w")
    # dictFile.write("userdict = {}\n")
    # dictFile.write("userdict['user'] = \"" + username + "\"\n")
    # dictFile.write("userdict['last-fetch'] = \"NULL\"\n")
    # dictFile.close()

    # create userdict to store to config.json
    dict_path = vcs_path + "/config.json"
    dictFile = open(dict_path, "w")
    userdict = {
        'user': username,
        'last-fetch': "NULL"
    }

    # write dict to json
    writejson(userdict, dictFile)
    dictFile.close()

    # read dict to check is data is same
    # dictFile = open(dict_path, "r")
    # data = readjson(dictFile)
    # print (data)

if __name__ == "__main__":
    main()
