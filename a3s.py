#!/usr/bin/env python3
"""Python-powered Arma3 Mod Downloader for Arma3Sync Repositorys"""

# Import Built-Ins
import glob
import os
import shutil
import sys
import zipfile
import getpass
import re
import subprocess
import distutils.dir_util
# import Other
import argparse
import fileinput
#from ftplib import FTP
import git
from pyunpack import Archive
from requests import get
# Import Locals
import EscapeAnsi
import console



def download(url, file_name, new_line=False):
    """download <URL> to <file_name>"""
    console.Output.debug("download " + url + " as " + file_name, new_line)
    with open(file_name, "wb") as download_file:
        response = get(url)
        download_file.write(response.content)

def update(output, dirs, enabled_sources, mod, **kwargs):
    # Manual downloaded Mods
    if mod[0] == "manual":
        displayname = mod[1]
        file_name = mod[2]
        output.printstatus("linking", displayname)
        if not os.path.islink(dirs["repo"] + "/@" + displayname):
            os.symlink(dirs["manual"] + "/" + file_name,
                       dirs["repo"] + "/@" + displayname)
    # Github Release
    if mod[0] == "github-release" and enabled_sources["github"]:
        displayname = mod[1]
        github_loc = mod[2]
        file_format = mod[3]
        cur_version = mod[4]
        output.printstatus(0, displayname)
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
            output.printstatus(1, displayname)
            return

        # Remove old Mod
        if os.path.isdir(os.path.join(dirs["mods"], "@" + displayname)):
            shutil.rmtree(os.path.join(dirs["mods"], "@" + displayname))

        # Download newest version
        zipname = file_format.replace("$version", new_version)
        savedfile = displayname + ".zip"
        output.debug("zipname: " + zipname + "; savedfile: " + savedfile)
        download("https://github.com/" + github_loc +
                 "/releases/download/" + new_tag + "/" + zipname,
                 savedfile)

        if not zipfile.is_zipfile(savedfile):
            output.printstatus(-1, displayname)
            return
        with zipfile.ZipFile(savedfile, "r") as packed:
            for zipinfo in packed.namelist():
                target_dir = packed.extract(zipinfo, dirs["mods"])
        target_dir = target_dir.replace(dirs["mods"], '')
        target_dir = target_dir.split('/')[1]
        output.debug("rename " + dirs["mods"] + "/" + target_dir + " to "
                     + dirs["mods"] + "/" + "@" + displayname)
        os.rename(dirs["mods"] + "/" + target_dir,
                  dirs["mods"] + "/" + "@" + displayname)
        os.remove(savedfile)  # Remove .zip file

        # Write new version to config
        old_line = ",".join([str(x) for x in mod])
        new_line = old_line.replace(cur_version, new_tag)
        for line in fileinput.input("repo.cfg", inplace=1):
            if old_line in line:
                line = line.replace(old_line, new_line)
            sys.stdout.write(line)

        # link mod to repo
        if not os.path.islink(dirs["repo"] + "/@" + displayname):
            output.printstatus("linking", displayname)
            os.symlink(dirs["mods"] + "/@" + displayname,
                       dirs["repo"] + "/@" + displayname)
        else:
            output.printstatus("is_linked", printstatus)

        output.printstatus(2, displayname)
    # Github
    if mod[0] == "github" and github_enabled:
        displayname = mod[1]
        github_loc = mod[2]
        output.printstatus(0, displayname)
        if os.path.isdir(displayname):
            modrepo = git.Repo(displayname)
            count = sum(1 for c in
                        modrepo.iter_commits('master..origin/master'))
            if count != 0:
                # Pull newest version from remote
                modrepo.remotes.origin.pull()
            elif not args.skip_version:
                # No update needed
                output.printstatus(1, displayname)
                return
        else:
            modrepo = git.Repo.clone_from("https://github.com/" +
                                          github_loc + ".git",
                                          displayname)
            for mod_file in glob.glob(displayname + r"/@*"):
                shutil.move(mod_file, moddir + "/" + displayname)

        output.printstatus(2, displayname)
    if mod[0] == "curl_biggest_zip" and curl_enabled:
        displayname = mod[1]
        url = mod[2]
        curl_version = mod[3]
        new_version = str()
        savedfile = displayname + ".zip"

        output.printstatus(0, displayname)
        download(url, "/tmp/" + displayname + ".tmp")
        with open("/tmp/" + displayname + ".tmp", "r") as page:
            versions = list()
            for line in page:
                line = re.findall(curl_version, line)
                if line:
                    line = line[0].split('"')[0]
                    versions.append(line)
            versions.sort(reverse=True)
            new_version = versions[0]
        download(os.path.join(url, new_version), savedfile)
        if not zipfile.is_zipfile(savedfile):
            output.printstatus(-1, displayname)
            return
        target_dir = str()
        with zipfile.ZipFile(savedfile, "r") as packed:
            for zipinfo in packed.namelist():
                target_dir = packed.extract(zipinfo, moddir)
        os.remove(savedfile)
        output.printstatus(2, displayname)
    if mod[0] == "curl_biggest_rar" and curl_enabled:
        displayname = mod[1]
        url = mod[2]
        curl_version = mod[3]
        new_version = str()
        savedfile = displayname + ".rar"

        output.printstatus(0, displayname)
        download(url, "/tmp/" + displayname + ".tmp")
        output.debug("looking for" + curl_version)
        with open("/tmp/" + displayname + ".tmp", "r") as page:
            versions = list()
            for line in page:
                line = re.findall(curl_version, line)
                if line:
                    line = line[0].split('"')[0]
                    versions.append(line)
            versions.sort(reverse=True)
            new_version = versions[0]
            output.debug("found version: " + new_version)
        download(os.path.join(url, new_version), savedfile)
        Archive(savedfile).extractall(moddir)
        os.remove(savedfile)
        output.printstatus(2, displayname)
    if mod[0] == "curl_folder" and curl_enabled:
        displayname = mod[1]
        url = mod[2]
        path = mod[2].split("//")[1]
        output.printstatus(0, displayname)
        if path.endswith("/"):
            path = path[:-1]
        os.system("wget -qq -r " + url)
        output.debug("copytree " + path + " --> " + moddir + "/"
                     + "@" + displayname)
        distutils.dir_util.copy_tree(path, moddir + "/" +
                                     "@" + displayname)
        shutil.rmtree(path)
        output.printstatus(2, displayname)


def get_sources(args):
    """get all source flags from args and return as dict"""
    enabled_sources = {"github": True,
                       "workshop": True,
                       "ace_optionals": True,
                       "curl": True}
    if args.workshop_only:
        enabled_sources["github"] = False
        enabled_sources["ace_optionals"] = False
        enabled_sources["curl"] = False
    if args.no_workshop:
        enabled_sources["workshop"] = False
    if args.no_github:
        enabled_sources["github"] = False
    if args.no_ace_optionals:
        enabled_sources["ace_optionals"] = False
    return enabled_sources


def get_dirs(output, modlist):
    """get dirs from modlist"""
    dirs = {"mods": os.getcwd(),
            "repo": os.getcwd(),
            "steamcmd": os.getcwd(),
            "steamdownload": os.getcwd(),
            "manual": os.getcwd()}
    for mod in modlist:
        if mod[0] == "repolocation":
            dirs["mods"] = mod[1]
            output.debug("repo: " + dirs["mods"])
            continue
        if mod[0] == "steamcmd":
            dirs["steamcmd"] = mod[1]
            dirs["steamdownload"] = mod[2]
            output.debug("steamcmd: " + dirs["steamcmd"] +
                         " steamdownload: " + dirs["steamdownload"])
            continue
        if mod[0] == "manual_location":
            dirs["manual"] = mod[1]
            output.debug("Manual mods: " + dirs["manual"])
            continue
    return dirs

def rm_all_symlinks(directory):
    """remove all symlinks in directory"""
    for root, dirs, files in os.walk(directory):
        if root.startswith("."):
            # Ignore hidden directorys
            continue
        for filename in files:
            path = os.path.join(root, filename)
            if os.path.islink(path):
                os.unlink(path)
            else:
                # If it's not a symlink we're not interested.
                continue
        for dirname in dirs:
            path = os.path.join(root, dirname)
            if os.path.islink(path):
                os.unlink(path)
            else:
                # If it's not a symlink we're not interested.
                continue



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

    enabled_sources = get_sources(args)

    # Read existing config
    modlist = list()
    with open("repo.cfg", "r") as conf:
        for line in conf:
            if line.startswith("#"):
                continue
            modlist.append(line.strip("\n").split(","))

    # Locate saving directory for installed mods
    dirs = get_dirs(output, modlist)

    workshop_ids = list()
    workshop_names = list()
    ace_optional_files = list()
    for mod in modlist:
        if args.update:
            rm_all_symlinks(dirs["repo"])
            kargs = {"skip_version":args.skip_version}
            update(output, dirs, enabled_sources, mod, kwargs=kargs)
            # ace_optionals
            if mod[0] == "ace_optionals" and enabled_sources["ace_optionals"]:
                ace_optional_files.append(mod[1])
                output.printstatus(4, mod[1])
            # Steam Workshop
            if mod[0] == "steam" and enabled_sources["workshop"]:
                workshop_names.append(mod[1])
                workshop_ids.append(mod[2])
                output.printstatus(3, mod[1])

    # Steam Workshop
    if args.workshop_reset:
        os.remove("/home/arma3/steamcmd/steamapps/" +
                  "workshop/appworkshop_107410.acf")  # make path relative

    if args.update and enabled_sources["workshop"]:
        is_failed = True
        while is_failed:
            is_failed = False
            with open("/tmp/steambag.tmp", "wb") as steambag:
                output.printstatus(5)
                login = input("Login: ")
                passwd = getpass.getpass()
                steamguard = input("Steam Guard Code: ")

                steambag.write(bytes("login " + login + " " + passwd +
                                     " " + steamguard + "\n", 'UTF-8'))

                cursor_up_one = '\x1b[1A'
                erase_line = '\x1b[2K'
                for i in range(3):  # remove written stuff
                    print(cursor_up_one + erase_line + cursor_up_one)
                # test if bytes can be removed
                steambag.write("@nCSClientRateLimitKbps 50000\n")
                steambag.write("@ShutdownOnFailedCommand 1\n")
                steambag.write("DepotDownloadProgressTimeout 90000\n")
                for workshop_id in workshop_ids:
                    steambag.write("workshop_download_item 107410 "
                                   + workshop_id + " validate" + "\n")
                    output.debug("wrote " + workshop_id + " to steambag")
                steambag.write("quit")

            output.debug("run \'" + dirs["steamcmd"]
                         + " +runscript /tmp/steambag.tmp\'")
            if args.security == 1:
                sys.stdout.write("\rHide Text for security reasons." +
                                 "THX VOLVO! (disable with --security 0)" +
                                 ansi_escape.HIDDEN + "\n")
                sys.stdout.write("\rThis does not seem to be working. " +
                                 "Please use --security 2 instead\n")
            if args.security == 2:
                output.debug("redirect steam output to /dev/null")
                sys.stdout.write("\rVoiding Steam Output.\n" +
                                 "\tWARNING! This is of no means safe!\n")
                os.system("bash " + dirs["steamcmd"]
                          + " +runscript /tmp/steambag.tmp" + ">> /dev/null")
            else:
                os.system("bash " + dirs["steamcmd"]
                          + " +runscript /tmp/steambag.tmp")

            sys.stdout.write(ansi_escape.HIDDEN_OFF)
            output.debug("remove steambag")
            os.remove("/tmp/steambag.tmp")

            for i, _ in enumerate(workshop_ids):
                if not os.path.isdir(dirs["steamdownload"] + "/"
                                     + workshop_ids[i]):
                    output.printstatus("err_not_exist", workshop_names[i])
                    output.printstatus("err_steam", workshop_ids[i])
                    is_failed = True
                    continue
                if os.path.islink(dirs["repo"] + "/@" + workshop_names[i]):
                    output.printstatus("is_linked", dirs["repo"] + "/@"
                                       + workshop_names[i])
                    continue

                output.debug("create symlink " + dirs["repo"] + "/@"
                             + workshop_names[i] + " -> "
                             + dirs["steamdownload"]
                             + "/" + workshop_ids[i])
                os.symlink(dirs["steamdownload"] + "/" + workshop_ids[i],
                           dirs["repo"] + "/@" + workshop_names[i])
                output.printstatus(2, workshop_names[i])
            output.printstatus(2, "Steam Workshop")
            if is_failed:
                sys.stdout.write("Workshop Update seems to have failed.")
                out = input("Try Again? (y/N)")
                if out.upper() == "Y":
                    is_failed = False



    # ace_optionals
    if args.update and enabled_sources["ace_optionals"]:
        if os.path.isdir(dirs["mods"] + "/@ace_optionals"):
            output.debug("existing @ace_optionals found. removing old files")
            shutil.rmtree(dirs["mods"] + "/@ace_optionals")
        os.makedirs(dirs["mods"] + "/@ace_optionals/addons")
        for mod in ace_optional_files:
            output.debug("looking for " + dirs["mods"] + "/@ACE3/optionals/*"
                         + mod + "*")
            for file in glob.glob(dirs["mods"] + "/@ACE3/optionals/*"
                                  + mod + "*"):
                output.debug("found " + file)
                if os.path.isdir(file):
                    output.debug("copy " + file + " to "
                                 + dirs["mods"] + "/@ace_optionals/addons/"
                                 + os.path.basename(file))
                    shutil.copytree(file,
                                    dirs["mods"] + "/@ace_optionals/addons/" +
                                    os.path.basename(file))
                elif os.path.isfile(file):
                    output.debug("copy " + file + " to "
                                 + dirs["mods"] + "/@ace_optionals/addons/"
                                 + os.path.basename(file))
                    shutil.copy(file,
                                dirs["mods"] + "/@ace_optionals/addons/" +
                                os.path.basename(file))
                else:
                    output.printstatus("err_not_exist", file)
        output.printstatus("success_update", "@ace_optionals")

    # make apache like our mods
    if args.update and False:
        for root, _, _ in os.walk(dirs["moddir"]):
            if not root == ".a3s":
                os.chmod(root, 0o755)
        return


if __name__ == "__main__":
    main()
