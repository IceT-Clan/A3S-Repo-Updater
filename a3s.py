#!/usr/bin/env python3
"""Python-powered Arma3 Mod Downloader for Arma3Sync Repositorys"""

# Import Built-Ins
import glob
import os
import shutil
import sys
# import zipfile
import getpass
import re
import subprocess
import distutils.dir_util
# import Other
import argparse
import fileinput
# from ftplib import FTP
import git
import magic
from pyunpack import Archive
# Import Locals
import EscapeAnsi
import console
import secret
from misc import (download, gglob, link_to, pls_copy, read_config, get_dirs,
                  rm_all_symlinks, get_sources)


def updater_update(output):
    """update the updater"""
    branch = "development"
    u_git = git.Git("./")
    u_git.init()
    output.debug("current branch: " + u_git.branch())
    if not u_git.branch_name == branch:
        u_git.checkout(branch)

    try:
        u_git.pull()
    except Exception as exp:
        output.debug("Exception:" + exp)
        raise exp
    else:
        u_git.stash()


def update(output, dirs, enabled_sources, mod, **kwargs):
    """update mods with given information"""
    # Manual downloaded Mods
    if mod[0] == "manual":
        displayname = mod[1]
        file_name = mod[2]

        output.printstatus("linking", displayname)
        if not os.path.islink(dirs["repo"] + "/@" + displayname):
            output.printstatus("linking", displayname)
            os.symlink(dirs["manual"] + "/" + file_name,
                       dirs["repo"] + "/@" + displayname)
        else:
            output.printstatus("is_linked", displayname)

    # Github Release
    elif mod[0] == "github-release" and enabled_sources["github"]:
        displayname = mod[1]
        github_loc = mod[2]
        file_format = mod[3]
        cur_version = mod[4]

        output.printstatus("updating", displayname)
        if os.path.isdir(displayname):
            modrepo = git.Repo(displayname)
            modrepo.remotes.origin.pull()
        else:
            modrepo = git.Repo.clone_from("https://github.com/" +
                                          github_loc + ".git",
                                          displayname)

        # Check if an update is available
        new_tag = subprocess.check_output(["git", "-C", displayname,
                                           "describe", "--abbrev=0",
                                           "--tags"])
        new_tag = new_tag.decode("UTF-8")
        new_tag = new_tag[:-1]
        new_version = new_tag
        if new_tag.startswith("v"):
            new_version = new_tag[1:]
        if new_tag == cur_version and not kwargs["skip_version"]:
            # No update needed
            output.printstatus("is_up_to_date", displayname)
            return

        # Remove old Mod
        output.debug("removing " +
                     os.path.join(dirs["mods"], "@" + displayname), True)
        if os.path.isdir(os.path.join(dirs["mods"], "@" + displayname)):
            shutil.rmtree(os.path.join(dirs["mods"], "@" + displayname))

        # Download newest version
        zipname = file_format.replace("$version", new_version)
        savedfile = displayname + ".zip"
        output.debug("zipname: " + zipname + "; savedfile: " + savedfile)
        download(output, "https://github.com/" + github_loc +
                 "/releases/download/" + new_tag + "/" + zipname,
                 savedfile)

        # extract <savedfile>
        Archive(savedfile).extractall(dirs["mods"])

        # Remove .zip file
        os.remove(savedfile)

        # Write new version to config
        old_line = ",".join([str(x) for x in mod])
        new_line = old_line.replace(cur_version, new_tag)
        for line in fileinput.input("repo.cfg", inplace=1):
            if old_line in line:
                line = line.replace(old_line, new_line)
            sys.stdout.write(line)
        output.printstatus("success_update", displayname)

        # link moddir/@mod to repo/@mod
        link_to(output, dirs["mods"], dirs["repo"], displayname)

    # Github
    elif mod[0] == "github" and enabled_sources["github"]:
        displayname = mod[1]
        github_loc = mod[2]
        output.printstatus("updating", displayname)

        if os.path.isdir(displayname):
            modrepo = git.Repo(displayname)
            count = sum(1 for c in
                        modrepo.iter_commits('master..origin/master'))
            if count != 0:
                # Pull newest version from remote
                modrepo.remotes.origin.pull()
            elif not kwargs["skip_version"]:
                # No update needed
                output.printstatus("is_up_to_date", displayname)
                return
        else:
            modrepo = git.Repo.clone_from("https://github.com/" +
                                          github_loc + ".git",
                                          displayname)
            for mod_file in glob.glob(displayname + r"/@*"):
                shutil.move(mod_file, dirs["mods"] + "/" + displayname)
        output.printstatus("success_update", displayname)

        # link moddir/@mod to repo/@mod
        link_to(output, dirs["mods"], dirs["repo"], displayname)

    # download html file; grep regex; get biggest number;
    #  download found file; extract;
    elif mod[0] == "curl_biggest_archive" and enabled_sources["curl"]:
        displayname = mod[1]
        url = mod[2]
        curl_version = mod[3]
        new_version = str()
        savedfile = displayname + ".archive"

        output.printstatus("updating", displayname)
        download(output, url, "/tmp/" + displayname + ".tmp", True)
        with open("/tmp/" + displayname + ".tmp", "r") as page:
            versions = list()
            for line in page:
                line = re.findall(curl_version, line)
                if line:
                    line = line[0].split('"')[0]
                    versions.append(line)
            versions.sort(reverse=True)
            new_version = versions[0]
        download(output, os.path.join(url, new_version), savedfile)

        # get file type of <savedfile>
        header = magic.from_file(savedfile).split(",")[0]
        output.debug("File is :" + header)

        # only continue if file type is an archive
        if "archive" not in header:
            output.printstatus("err_not_valid", "archive", displayname)
            return
        output.debug("found file type '" + header + "' for file " + savedfile)

        if "Java" in header:
            secret.android()
            return
        output.debug("inflating " + savedfile)

        # extract <savedfile> to <dirs["mods"]>
        Archive(savedfile).extractall(dirs["mods"])

        # Cleanup
        os.remove("/tmp/" + displayname + ".tmp")
        os.remove(savedfile)

        output.printstatus("success_update", displayname)

        # link moddir/@mod to repo/@mod
        link_to(output, dirs["mods"], dirs["repo"], displayname)

    elif mod[0] == "curl_folder" and enabled_sources["curl"]:
        displayname = mod[1]
        url = mod[2]
        path = mod[2].split("//")[1]

        output.printstatus("updating", displayname)

        if path.endswith("/"):
            path = path[:-1]

        output.debug("wget " + url, True)
        os.system("wget -q -r " + url)
        output.debug("copytree " + path + " --> " + dirs["mods"] + "/@" +
                     displayname)
        distutils.dir_util.copy_tree(path, dirs["mods"] + "/" +
                                     "@" + displayname)
        shutil.rmtree(path)
        output.printstatus("success_update", displayname)

        # link moddir/@mod to repo/@mod
        link_to(output, dirs["mods"], dirs["repo"], displayname)


def main():
    """main"""
    ansi_escape = EscapeAnsi.EscapeAnsi()

    # Command line argument setup
    parser = argparse.ArgumentParser(description="ArmA 3 Repository Updater")
    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument("-v", "--version",
                        action="version", version='%(prog)s 0.2.0')
    parser.add_argument("-d", "--debug",
                        help="enable debug",
                        action="store_true")

    group.add_argument("-a", "--add", action="store_true",
                       help="Add mod to repository")
    group.add_argument("-r", "--remove", action="store_true",
                       help="Remove mod from repository")
    group.add_argument("-u", "--update", action="store_true",
                       help="Update repository")

    parser.add_argument("--security", type=int, default=2,
                        help="set security level")
    parser.add_argument("--ignore-version", action="store_true",
                        help="ignore version checking", dest="skip_version")
    parser.add_argument("--reset-steam", action="store_true",
                        help="reset Steam to redownload all files",
                        dest="workshop_reset")

    parser.add_argument("--steam-only", action="store_true",
                        help="update only Steam Workshop Mods",
                        dest="workshop_only")
    parser.add_argument("--no-steam", action="store_true",
                        help="do not update Steam Workshop Mods",
                        dest="no_workshop")
    parser.add_argument("--no-github", action="store_true",
                        help="do not update Github Mods",
                        dest="no_github")
    parser.add_argument("--no-ace-optionals", action="store_true",
                        help="do not generate new ace_optionals",
                        dest="no_ace_optionals")

    args = parser.parse_args()

    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit(2)

    output = console.Output(args.debug)
    output.debug("enabled")

    if args.security > 2:
        args.security = 2

    output.debug(args)

    # get enabled sources
    enabled_sources = get_sources(args)

    # Read existing config
    modlist = read_config("repo.cfg")

    # Locate saving directory for installed mods
    dirs = get_dirs(output, modlist)

    workshop_ids = list()
    workshop_names = list()
    ace_optional_files = list()
    for mod in modlist:
        if args.update:
            rm_all_symlinks(dirs["repo"])
            update(output, dirs, enabled_sources, mod,
                   skip_version=args.skip_version)
            # ace_optionals
            if mod[0] == "ace_optionals" and enabled_sources["ace_optionals"]:
                ace_optional_files.append(mod[1])
                output.printstatus("ace_opt_add", mod[1])
            # Steam Workshop
            if mod[0] == "steam" and enabled_sources["workshop"]:
                workshop_names.append(mod[1])
                workshop_ids.append(mod[2])
                output.printstatus("steambag_add", mod[1])

    # Steam Workshop
    if args.workshop_reset:
        output.printstatus("success_removed",
                           "/home/arma3/steamcmd/steamapps/" +
                           "workshop/appworkshop_107410.acf")
        os.remove("/home/arma3/steamcmd/steamapps/" +
                  "workshop/appworkshop_107410.acf")  # make path relative

    if args.update and enabled_sources["workshop"]:
        is_failed = True
        while is_failed:
            is_failed = False
            with open("/tmp/steambag.tmp", "wb") as steambag:
                output.printstatus("do_workshop")
                login = input()("Login: ")
                passwd = getpass.getpass()
                steamguard = input("Steam Guard Code: ")

                steambag.write("login " + login + " " + passwd + " " +
                               steamguard + "\n")

                # remove ugly login print
                cursor_up_one = '\x1b[1A'
                erase_line = '\x1b[2K'
                for i in range(3):
                    print(cursor_up_one + erase_line + cursor_up_one)

                # add stuff 'cause steam
                steambag.write("@nCSClientRateLimitKbps 50000\n")
                steambag.write("@ShutdownOnFailedCommand 1\n")
                steambag.write("DepotDownloadProgressTimeout 90000\n")
                for workshop_id in workshop_ids:
                    steambag.write("workshop_download_item 107410 " +
                                   workshop_id + " validate" + "\n")
                    output.debug("wrote " + workshop_id + " to steambag")
                steambag.write("quit")

            output.debug("run \'" + dirs["steamcmd"] +
                         " +runscript /tmp/steambag.tmp\'")
            if args.security == 1:
                sys.stdout.write("\rHide Text for security reasons." +
                                 "THX VOLVO! (disable with --security 0)" +
                                 ansi_escape.HIDDEN + "\n")
                sys.stdout.write("\rThis does not seem to be working. " +
                                 "Please use --security 2 instead\n")
            elif args.security == 2:
                output.debug("redirect steam output to /dev/null")
                sys.stdout.write("\rVoiding Steam Output.\n" +
                                 "\tWARNING! This is of no means safe!\n")
                os.system("bash " + dirs["steamcmd"] +
                          " +runscript /tmp/steambag.tmp" + ">> /dev/null")
            else:
                os.system("bash " + dirs["steamcmd"] +
                          " +runscript /tmp/steambag.tmp")

            sys.stdout.write(ansi_escape.HIDDEN_OFF)
            output.debug("remove steambag")
            os.remove("/tmp/steambag.tmp")

            for i, _ in enumerate(workshop_ids):
                if not os.path.isdir(dirs["steamdownload"] + "/" +
                                     workshop_ids[i]):
                    output.printstatus("err_not_exist", workshop_names[i])
                    output.printstatus("err_steam", workshop_ids[i])
                    is_failed = True
                    continue
                if os.path.islink(dirs["repo"] + "/@" + workshop_names[i]):
                    output.printstatus("is_linked", dirs["repo"] + "/@" +
                                       workshop_names[i])
                    continue

                output.debug("create symlink " + dirs["repo"] + "/@" +
                             workshop_names[i] + " -> " +
                             dirs["steamdownload"] + "/" + workshop_ids[i])
                os.symlink(dirs["steamdownload"] + "/" + workshop_ids[i],
                           dirs["repo"] + "/@" + workshop_names[i])
                output.printstatus("success_linking", workshop_names[i])
            if is_failed:
                sys.stdout.write("Workshop Update seems to have failed.")
                out = input("Try Again? (y/N)")
                if out.upper() == "Y":
                    is_failed = False
            output.printstatus("success_update", "Steam Workshop")

    # ace_optionals
    if args.update and enabled_sources["ace_optionals"]:
        if os.path.isdir(dirs["mods"] + "/@ace_optionals"):
            output.debug("existing @ace_optionals found. removing old files")
            shutil.rmtree(dirs["mods"] + "/@ace_optionals")
        os.makedirs(dirs["mods"] + "/@ace_optionals/addons")
        for mod in ace_optional_files:
            output.debug("looking for " + dirs["mods"] + "/@ACE3/optionals/*" +
                         mod + "*")
            for file in gglob(dirs["mods"] + "/@ACE3/optionals/*" +
                              mod + "*"):
                output.debug("found " + file)
                pls_copy(output, file, dirs["mods"] +
                         "/@ace_optionals/addons/" + os.path.basename(file))
        output.printstatus("success_update", "@ace_optionals")

    # make apache like our mods
    if args.update and False:
        for root, _, _ in os.walk(dirs["moddir"]):
            if not root == ".a3s":
                os.chmod(root, 0o755)
        return


if __name__ == "__main__":
    main()
