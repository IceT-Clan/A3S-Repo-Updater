#!/usr/bin/env python3
"""Python-powered Arma3 Mod Downloader for Arma3Sync Repositorys"""

import argparse
import fileinput
import git
import glob
import os
import shutil
import sys
import zipfile
import getpass
import re
import subprocess
import distutils.dir_util

from pyunpack import Archive
from requests import get
from ftplib import FTP

class VT100Formats:
    """http://misc.flogisoft.com/bash/tip_colors_and_formatting
        ANSI/VT100 colors and formats"""

    # formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    STANDOUT = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    FORMAT_6 = '\033[6m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'

    RESET = '\033[m'

    BOLD_OFF = '\033[21m'
    DIM_OFF = '\033[22m'
    STANDOUT_OFF = '\033[23m'
    UNDERLINE_OFF = '\033[24m'
    BLINK_OFF = '\033[25m'
    FORMAT_6_OFF = '\033[26m'
    REVERSE_OFF = '\033[27m'
    HIDDEN_OFF = '\033[28m'

    # 8 foreground colors
    F_COLOR_OFF = '\033[39m'
    F_BLACK = '\033[30m'
    F_RED = '\033[31m'
    F_GREEN = '\033[32m'
    F_YELLOW = '\033[33m'
    F_BLUE = '\033[34m'
    F_MAGENTA = '\033[35m'
    F_CYAN = '\033[36m'

    F_L_GRAY = '\033[37m'
    F_GRAY = '\033[90m'

    F_L_RED = '\033[91m'
    F_L_GREEN = '\033[92m'
    F_L_YELLOW = '\033[93m'
    F_L_BLUE = '\033[94m'
    F_L_MAGENTA = '\033[95m'
    F_L_CYAN = '\033[96m'

    F_WHITE = '\033[97m'

    # 8 background colors
    B_COLOR_OFF = '\033[49m'
    B_BLACK = '\033[40m'
    B_RED = '\033[41m'
    B_GREEN = '\033[42m'
    B_YELLOW = '\033[43m'
    B_BLUE = '\033[44m'
    B_MAGENTA = '\033[45m'
    B_CYAN = '\033[46m'

    B_L_GRAY = '\033[47m'
    B_GRAY = '\033[100m'

    B_L_RED = '\033[101m'
    B_L_GREEN = '\033[102m'
    B_L_YELLOW = '\033[103m'
    B_L_BLUE = '\033[104m'
    B_L_MAGENTA = '\033[105m'
    B_L_CYAN = '\033[106m'

    B_WHITE = '\033[107m'

    F_COLOR_INIT = '\033[38;5;'
    B_COLOR_INIT = '\033[48;5;'

    # 256 forground colors
    def f_color(self, color_number):
        """print foreground color switch"""
        return self.F_COLOR_INIT + color_number + 'm'

    # 256 background colors
    def b_color(self, color_number):
        """print background color switch"""
        return self.B_COLOR_INIT + color_number + 'm'


def download(url, file_name):
    """download url to file_name"""
    debug("download " + url + " as " + file_name, True)
    with open(file_name, "wb") as download_file:
        response = get(url)
        download_file.write(response.content)


def printstatus(state, displayname="NO DISPLAY NAME"):
    """print a staus state with displayname"""
    if state == 0:
        # Updating
        sys.stdout.write("\r" + "[ " + VT100Formats.F_L_YELLOW + "WAIT"
                         + VT100Formats.RESET + " ] " + "Updating " +
                         displayname + "...")
    elif state == 1:
        sys.stdout.write("\r" + "[  " + VT100Formats.F_L_GREEN + "OK"
                         + VT100Formats.RESET + "  ] " + displayname +
                         " is up to date" + "\n")
    elif state == 2:
        sys.stdout.write("\r" + "[  " + VT100Formats.F_L_GREEN + "OK"
                         + VT100Formats.RESET + "  ] " + displayname
                         + " successfully updated" + "\n")
    elif state == 3:
        sys.stdout.write("\r" + "[  " + VT100Formats.F_L_BLUE + "OK"
                         + VT100Formats.RESET + "  ] " + displayname +
                         " has been added to the Steam Bag" + "\n")
    elif state == 4:
        sys.stdout.write("\r" + "[  " + VT100Formats.F_L_BLUE + "OK"
                         + VT100Formats.RESET + "  ] " + displayname +
                         " will be added to @ace_optinals" + "\n")
    elif state == 5:
        sys.stdout.write("\r" + "[ " + VT100Formats.F_L_YELLOW + "WAIT"
                         + VT100Formats.RESET + " ] " +
                         "doing Steam Workshop" + "\n")
    elif state == 6:
        sys.stdout.write("\r" + "[ " + VT100Formats.F_L_BLUE + "SKIP"
                         + VT100Formats.RESET + " ] " + displayname +
                         " is already linked" + "\n")
    elif state == -1:
        sys.stdout.write("\r" + "[ " + VT100Formats.F_L_RED + "FAIL"
                         + VT100Formats.RESET + " ] " + displayname +
                         " is not a valid ZIP-Archive" + "\n")
    elif state == -2:
        sys.stdout.write("\r" + "[ " + VT100Formats.F_L_RED + "FAIL"
                         + VT100Formats.RESET + " ] " + displayname +
                         " does not exist" + "\n")
    elif state == -3:
        sys.stdout.write("\r" + "[ " + VT100Formats.F_L_RED + "FAIL"
                         + VT100Formats.RESET + " ] " +
                         "Maybe SteamCMD did not download " + displayname +
                         " correctly? " +
                         "(use --steam-only to skip other sources)" + "\n")
    elif state == -4:
        sys.stdout.write("\r" + "[ " + VT100Formats.F_L_RED + "FAIL"
                         + VT100Formats.RESET + " ] " + displayname +
                         " is not a valid RAR-Archive" + "\n")


def debug(msg, add_newline=False):
    """print debug messages"""
    if add_newline:
        newline = "\n"
    else:
        newline = ""
    if is_debug:
        sys.stdout.write(newline + "[" + VT100Formats.BOLD + "DEBUG"
                         + VT100Formats.RESET + "] " + str(msg) + "\n")


def main():
    """main"""
    workshop_ids = list()
    workshop_names = list()
    ace_optional_files = list()

    # Command line argument setup
    parser = argparse.ArgumentParser(description="Arma 3 Repository Updater")
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

    parser.add_argument("--security", type=int, default=1,
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

    is_debug = args.debug
    debug("enabled")

    if args.security > 2:
        args.security = 2

    if is_debug:
        debug(args)

    github_enabled = True
    workshop_enabled = True
    ace_optionals_enabled = True
    if args.workshop_only:
        github_enabled = False
        ace_optionals_enabled = False
    if args.no_workshop:
        workshop_enabled = False
    if args.no_github:
        github_enabled = False
    if args.no_ace_optionals:
        ace_optionals_enabled = False

    # Read existing config
    modlist = list()
    with open("repo.cfg", "r") as conf:
        for line in conf:
            if line.startswith("#"):
                continue
            modlist.append(line.strip("\n").split(","))

    # Locate saving directory for installed mods
    moddir = os.getcwd()
    for mod in modlist:
        if mod[0] == "repolocation":
            moddir = mod[1]
            debug("Repo:" + moddir)
            continue
        if mod[0] == "steamcmd":
            steamcmd = mod[1]
            steamdownload = mod[2]
            debug("steamcmd:" + steamcmd +
                  " steamdownload:" + steamdownload)
            continue
        if args.update:
            # Github Release
            if mod[0] == "github-release" and github_enabled:
                displayname = mod[1]
                github_loc = mod[2]
                file_format = mod[3]
                cur_version = mod[4]
                printstatus(0, displayname)
                if os.path.isdir(displayname):
                    modrepo = git.Repo(displayname)
                    modrepo.remotes.origin.pull()
                else:
                    modrepo = git.Repo.clone_from("https://github.com/"
                                                  + github_loc + ".git",
                                                  displayname)

                # Check if an update is available
                new_tag = str(modrepo.tags[-1])
                new_version = new_tag
                if new_tag.startswith("v"):
                    new_version = new_tag[1:]
                if new_tag == cur_version and not args.skip_version:
                    # No update needed
                    printstatus(1, displayname)
                    continue

                # Remove old Mod
                if os.path.isdir(os.path.join(moddir, "@" + displayname)):
                    shutil.rmtree(os.path.join(moddir, "@" + displayname))

                # Download newest version
                zipname = file_format.replace("$version", new_version)
                savedfile = displayname + ".zip"
                debug("zipname: " + zipname + "; savedfile: " + savedfile)
                """if args.debug: debug("download https://github.com/"
                                     + github_loc +
                                     "/releases/download/" + new_tag + "/"
                                     + zipname + " as " + savedfile)"""
                download("https://github.com/" + github_loc +
                         "/archive/" + new_tag + "/" + zipname,
                         savedfile)

                if not zipfile.is_zipfile(savedfile):
                    printstatus(-1, displayname)
                    continue
                target_dir = str()
                with zipfile.ZipFile(savedfile, "r") as packed:
                    for zipinfo in packed.namelist():
                        target_dir = packed.extract(zipinfo, moddir)
                target_dir = target_dir.replace(moddir, '')
                target_dir = target_dir.split('/')[1]
                debug("rename " + moddir + "/" + target_dir + " to " +
                      moddir + "/" + "@" + displayname)
                os.rename(moddir + "/" + target_dir,
                          moddir + "/" + "@" + displayname)
                os.remove(savedfile)  # Remove .zip file

                # Write new version to config
                old_line = ",".join([str(x) for x in mod])
                new_line = old_line.replace(cur_version, new_tag)
                for line in fileinput.input("repo.cfg", inplace=1):
                    if old_line in line:
                        line = line.replace(old_line, new_line)
                    sys.stdout.write(line)

                printstatus(2, displayname)
            # Github
            if mod[0] == "github" and github_enabled:
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
                    elif not args.skip_version:
                        # No update needed
                        printstatus(1, displayname)
                        continue
                else:
                    modrepo = git.Repo.clone_from("https://github.com/"
                                                  + github_loc + ".git",
                                                  displayname)
                    for mod_file in glob.glob(displayname + r"/@*"):
                        shutil.move(mod_file, moddir + "/" + displayname)

                printstatus(2, displayname)
            # ace_optionals
            if mod[0] == "ace_optionals" and ace_optionals_enabled:
                ace_optional_files.append(mod[1])
                printstatus(4, mod[1])
            # Steam Workshop
            if mod[0] == "steam" and workshop_enabled:
                workshop_names.append(mod[1])
                workshop_ids.append(mod[2])
                printstatus(3, mod[1])
            if mod[0] == "curl_biggest_zip":
                displayname = mod[1]
                url = mod[2]
                curl_version = mod[3]
                current_version = mod[4]
                new_version = str()
                savedfile = displayname + ".zip"

                printstatus(0, displayname)
                download(url, "/tmp/" + displayname + ".tmp")
                with open("/tmp/" + displayname + ".tmp", "r") as page:
                    versions = list()
                    for line in page:
                        line = re.findall(curl_version, line)
                        if line:
                            line = line[0].split('"')[0]
                            versions.append(line)
                    versions.append(current_version)
                    versions.sort(reverse=True)
                    new_version = versions[0]
                if current_version == new_version and not args.skip_version:
                    printstatus(1, displayname)
                    continue
                download(os.path.join(url, new_version), savedfile)
                if not zipfile.is_zipfile(savedfile):
                    printstatus(-1, displayname)
                    continue
                target_dir = str()
                with zipfile.ZipFile(savedfile, "r") as packed:
                    for zipinfo in packed.namelist():
                        target_dir = packed.extract(zipinfo, moddir)
                os.remove(savedfile)

                old_line = ",".join([str(x) for x in mod])
                new_line = old_line.replace(current_version, new_version)
                for line in fileinput.input("repo.cfg", inplace=1):
                    if old_line in line:
                        line = line.replace(old_line, new_line)
                    sys.stdout.write(line)
                printstatus(2, displayname)
            if mod[0] == "curl_biggest_rar":
                displayname = mod[1]
                url = mod[2]
                curl_version = mod[3]
                current_version = mod[4]
                new_version = str()
                savedfile = displayname + ".rar"

                printstatus(0, displayname)
                download(url, "/tmp/" + displayname + ".tmp")
                with open("/tmp/" + displayname + ".tmp", "r") as page:
                    versions = list()
                    for line in page:
                        line = re.findall(curl_version, line)
                        if line:
                            line = line[0].split('"')[0]
                            versions.append(line)
                    versions.append(current_version)
                    versions.sort(reverse=True)
                    new_version = versions[0]
                if current_version == new_version and not args.skip_version:
                    debug(current_version + " == " + new_version)
                    printstatus(1, displayname)
                    continue
                download(os.path.join(url, new_version), savedfile)
                Archive(savedfile).extractall(moddir)
                os.remove(savedfile)

                old_line = ",".join([str(x) for x in mod])
                new_line = old_line.replace(current_version, new_version)
                for line in fileinput.input("repo.cfg", inplace=1):
                    if old_line in line:
                        line = line.replace(old_line, new_line)
                    sys.stdout.write(line)
                printstatus(2, displayname)
            if mod[0] == "ftp_curl_biggest_torrent":
                displayname = mod[1]
                server = mod[2]
                target_dir = mod[3]
                curl_version = mod[4]
                current_version = mod[5]
                new_version = str()
                savedfile = displayname + ".torrent"

                printstatus(0, displayname)
                with FTP(server) as ftp:
                    ftp.login()
                    ftp.cwd(target_dir)
                    # lines = ftp.nlst()
                    lines = list()
                    ftp.dir('-t', lines.append)
                    ver_begin_i = curl_version.find("$version")
                    ver_bef = curl_version[:ver_begin_i]
                    ver_end_i = curl_version.find("$version") + len("$version")
                    ver_aftr = curl_version[ver_end_i:]
                    ver_bef_i = lines[0].find(ver_bef) + len(ver_bef)
                    ver_aftr_i = lines[0].find(ver_aftr)
                    lines[0] = lines[0][ver_bef_i:ver_aftr_i]
                    new_version = lines[0]
                    complete_file = curl_version.replace("$version",
                                                         new_version)

                    debug("send 'RETR %s" % complete_file + "' from '" +
                          target_dir + "' to '" + server +
                          "' and save answer to '" + savedfile + "'",
                          True)
                    ftp.retrbinary("RETR %s" % complete_file,
                                   open(savedfile, 'wb').write)
                # download torrent from savedfile
                os.system("python2 torrent.py " + savedfile + " ./")
            if mod[0] == "curl_folder":
                displayname = mod[1]
                url = mod[2]
                # path = mod[3]
                path = mod[2].split("//")[1]
                printstatus(0, displayname)
                if path.endswith("/"):
                    path = path[:-1]
                os.system("wget -qq -r " + url)
                debug("copytree " + path + " --> " + moddir + "/" +
                      "@" + displayname)
                distutils.dir_util.copy_tree(path, moddir + "/" +
                                             "@" + displayname)
                #                             path.split("/")[-1])
                shutil.rmtree(path)
                """shutil.move(moddir + "/" + path.split("/")[-1],
                            moddir + "/" + "@" + displayname)"""
                """subprocess.Popen(["mv", moddir + "/" + path.split("/")[-1],
                                moddir + "/" + "@" + displayname],
                                stdout=subprocess.PIPE)"""
                printstatus(2, displayname)

            # update loop done
        # loop done
    # loop complete

    # Steam Workshop
    if args.workshop_reset:
        os.remove("/home/arma3/steamcmd/steamapps/" +
                  "workshop/appworkshop_107410.acf")  # make path relative

    if args.update and workshop_enabled:
        with open("/tmp/steambag.tmp", "wb") as steambag:
            printstatus(5)
            login = input("Login: ")
            passwd = getpass.getpass()
            steamguard = input("Steam Guard Code: ")

            steambag.write(bytes("login " + login + " " + passwd +
                                 " " + steamguard + "\n", 'UTF-8'))

            CURSOR_UP_ONE = '\x1b[1A'
            ERASE_LINE = '\x1b[2K'
            for i in range(3):  # remove written stuff
                print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
            # test if bytes can be removed
            steambag.write(bytes("@nCSClientRateLimitKbps 50000\n", 'UTF-8'))
            steambag.write(bytes("@ShutdownOnFailedCommand 1\n", 'UTF-8'))
            steambag.write(bytes("DepotDownloadProgressTimeout 90000\n",
                                 'UTF-8'))
            for workshop_id in workshop_ids:
                steambag.write(bytes("workshop_download_item 107410 " +
                                     workshop_id + " validate" + "\n",
                                     'UTF-8'))
                debug("wrote " + workshop_id + " to steambag")
            steambag.write(bytes("quit", 'UTF-8'))

        debug("run \'" + steamcmd + " +runscript /tmp/steambag.tmp\'")
        if args.security == 1:
            sys.stdout.write("\rHide Text for security reasons. THX VOLVO! " +
                             "(disable with --security 0)" +
                             VT100Formats.HIDDEN + "\n")
            sys.stdout.write("\rThis does not seem to be working. " +
                             "Please use --security 2 instead\n")
        if args.security == 2:
            debug("redir steam output to /dev/null")
            sys.stdout.write("\rVoiding Steam Output.\n" +
                             "\tWARNING! This is of no means safe!\n")
            os.system("bash " + steamcmd + " +runscript /tmp/steambag.tmp" +
                      ">> /dev/null")
        else:
            os.system("bash " + steamcmd + " +runscript /tmp/steambag.tmp")

        sys.stdout.write(VT100Formats.HIDDEN_OFF)
        debug("remove steambag")
        os.remove("/tmp/steambag.tmp")

        for i in range(len(workshop_ids)):
            if not os.path.isdir(steamdownload + "/" + workshop_ids[i]):
                printstatus(-2, workshop_names[i])
                printstatus(-3, workshop_ids[i])
                continue
            if os.path.islink(moddir + "/@" + workshop_names[i]):
                printstatus(6, moddir + "/@" + workshop_names[i])
                continue

            debug("create symlink " + moddir + "/@" + workshop_names[i] +
                  " -> " + steamdownload + "/" + workshop_ids[i])
            os.symlink(steamdownload + "/" + workshop_ids[i],
                       moddir + "/@" + workshop_names[i])
            printstatus(2, workshop_names[i])
        printstatus(2, "Steam Workshop")

    # ace_optionals
    if args.update and ace_optionals_enabled:
        if os.path.isdir(moddir + "/@ace_optionals"):
            debug("existing @ace_optionals found. removing old files")
            shutil.rmtree(moddir + "/@ace_optionals")
        os.makedirs(moddir + "/@ace_optionals/addons")
        for mod in ace_optional_files:
            debug("looking for " + moddir + "/@ACE3/optionals/*" + mod + "*")
            for file in glob.glob(moddir + "/@ACE3/optionals/*" + mod + "*"):
                debug("found " + file)
                if os.path.isdir(file):
                    debug("copy " + file + " to " +
                          moddir + "/@ace_optionals/addons/" +
                          os.path.basename(file))
                    shutil.copytree(file,
                                    moddir + "/@ace_optionals/addons/" +
                                    os.path.basename(file))
                elif os.path.isfile(file):
                    debug("copy " + file + " to " +
                          moddir + "/@ace_optionals/addons/" +
                          os.path.basename(file))
                    shutil.copy(file,
                                moddir + "/@ace_optionals/addons/" +
                                os.path.basename(file))
                else:
                    printstatus(-2, file)
        printstatus(2, "@ace_optionals")

    return


if __name__ == "__main__":
    main()

