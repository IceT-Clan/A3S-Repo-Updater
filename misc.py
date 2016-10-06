"""misc functions"""
import os
import glob
import shutil
import subprocess
import requests
from tqdm import tqdm
from EscapeAnsi import EscapeAnsi as ansi_escape



def download(output, url, file_name, displayname, new_line=False, \
             hide=False):
    """download <URL> to <file_name>"""
    output.debug("download " + url + " as " + file_name, add_newline=new_line)
    cool_text = "\r" + "[ " + ansi_escape.F_L_YELLOW + "WAIT" \
                + ansi_escape.RESET + " ] " + "downloading "
                + displayname + "..."
    file_size = subprocess.check_output(["bash", "getURLength.sh", url])
    file_size = int(file_size.decode("UTF-8"))
    # output.debug("Length: " + file_size)
    with open(file_name, "wb") as download_file:
        if not hide:
            response = requests.get(url, stream=True)
            with open('output.bin', 'wb') as output:
                for data in tqdm(response.iter_content(1024), cool_text,
                                 file_size / 1024, unit="MB", unit_scale=True,
                                 leave=True):
                    download_file.write(data)
        else:
            response = requests.get(url)
            download_file.write(response.content)
    if not hide:
        print('\x1b[1A', end="")
        for _ in range(99):
            print('\x1b[1B', end="")


def link_to(output, src, dst, name):
    """link <src> to <dst> and print status via <output>"""
    if not os.path.islink(dst + "/@" + name):
        output.printstatus("linking", name)
        os.symlink(src + "/@" + name,
                   dst + "/@" + name)
    else:
        output.printstatus("is_linked", name)
    return


def read_config(repo):
    """read and return repo config"""
    modlist = list()
    with open(repo, "r") as conf:
        for line in conf:
            if line.startswith("#"):
                continue
            modlist.append(line.strip("\n").split(","))
    return modlist


def pls_copy(output, src, dst):
    """just copy src to dst"""
    if os.path.isdir(src):
        output.debug("copy " + src + " to " + dst)
        shutil.copytree(src, dst)
    elif os.path.isfile(src):
        output.debug("copy " + src + " to " + dst)
        shutil.copy(src, dst)
    else:
        output.printstatus("err_not_exist", src)


def gglob(pathname):
    """yes, glob.glob is too long"""
    return glob.glob(pathname)


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
            dirs["repo"] = mod[1]
            output.debug("repo: " + dirs["repo"])
            continue
        elif mod[0] == "modlocation":
            dirs["mods"] = mod[1]
            output.debug("mods: " + dirs["mods"])
            continue
        elif mod[0] == "steamcmd":
            dirs["steamcmd"] = mod[1]
            dirs["steamdownload"] = mod[2]
            output.debug("steamcmd: " + dirs["steamcmd"] +
                         " steamdownload: " + dirs["steamdownload"])
            continue
        elif mod[0] == "manual_location":
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
