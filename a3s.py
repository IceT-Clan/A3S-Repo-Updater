#!/usr/bin/env python3
import argparse
import fileinput
import git
import glob
import os
import shutil
import sys
import zipfile

from git import Repo
from requests import get


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def download(url, file_name):
    with open(file_name, "wb") as f:
        response = get(url)
        f.write(response.content)


def printstatus(state, displayname):
    if state == 0:
        # Updating
        sys.stdout.write("\r[" + bcolors.WARNING + "WAIT" + bcolors.ENDC +
                         "] Updating " + displayname + "...")
    elif state == 1:
        sys.stdout.write("\r[ " + bcolors.OKGREEN + "OK" + bcolors.ENDC +
                         " ] " + displayname + " is up to date\n")
    elif state == 2:
        sys.stdout.write("\r[ " + bcolors.OKGREEN + "OK" + bcolors.ENDC +
                         " ] " + displayname + " successfully updated\n")


def main():
    # Command line argument setup
    parser = argparse.ArgumentParser(description="Arma 3 Repository Updater")
    parser.add_argument("-a", "--add", action="store_true",
                        help="Add mod to repository")
    parser.add_argument("-r", "--remove", action="store_true",
                        help="Remove mod from repository")
    parser.add_argument("-u", "--update", action="store_true",
                        help="Update repository")

    args = parser.parse_args()

    # Read existing config
    modlist = list()
    with open("repo.cfg", "r") as conf:
        for line in conf:
            if line.startswith("#"):
                continue
            mod = line.strip("\n").split(",")
            modlist.append(mod)

    # Locate saving directory for installed mods
    moddir = os.getcwd()
    for mod in modlist:
        if mod[0] == "repolocation":
            moddir = mod[1]
            continue

        if args.update:
            if mod[0] == "github-release":
                displayname = mod[1]
                github_loc = mod[2]
                file_format = mod[3]
                cur_version = mod[4]
                printstatus(0, displayname)
                if os.path.isdir(displayname):
                    modrepo = git.Repo(displayname)
                    modrepo.remotes.origin.pull()
                else:
                    modrepo = Repo.clone_from("https://github.com/"
                                              + github_loc + ".git",
                                              displayname)

                # Check if an update is available
                new_tag = str(modrepo.tags[-1])
                new_version = new_tag
                if new_tag.startswith("v"):
                    new_version = new_tag[1:]
                if new_tag == cur_version:
                    # No update needed
                    printstatus(1, displayname)
                    continue

                # Download newest version
                zipname = file_format.replace("$version", new_version)
                savedfile = displayname + ".zip"
                download("https://github.com/" + github_loc +
                         "/releases/download/" + new_tag + "/" + zipname,
                         savedfile)
                with zipfile.ZipFile(savedfile, "r") as z:
                    z.extractall(moddir)
                os.remove(savedfile)  # Remove .zip file

                # Write new version to config
                old_line = ",".join([str(x) for x in mod])
                new_line = old_line.replace(cur_version, new_tag)
                for line in fileinput.input("repo.cfg", inplace=1):
                    if old_line in line:
                        line = line.replace(old_line, new_line)
                    sys.stdout.write(line)

                printstatus(2, displayname)
            if mod[0] == "github":
                displayname = mod[1]
                github_loc = mod[2]
                printstatus(0, displayname)
                if os.path.isdir(displayname):
                    modrepo = git.Repo(displayname)
                    count = sum(1 for c in
                                modrepo.iter_commits('master..origin/master'))
                    if count != 0:
                        # Pull newest version from remote
                        modrepo.remotes.origin.pull()
                    else:
                        # No update needed
                        printstatus(1, displayname)
                        continue
                else:
                    modrepo = Repo.clone_from("https://github.com/"
                                              + github_loc + ".git",
                                              displayname)
                    for f in glob.glob(displayname + r"/@*"):
                        shutil.move(f, moddir + "/" + displayname)

                printstatus(2, displayname)

    return

if __name__ == "__main__":
    main()
