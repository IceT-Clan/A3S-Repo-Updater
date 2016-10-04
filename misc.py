"""misc functions"""
import os
import glob
import shutil
from requests import get
import console


def download(url, file_name, new_line=False):
    """download <URL> to <file_name>"""
    console.Output.debug("download " + url + " as " + file_name, new_line)
    with open(file_name, "wb") as download_file:
        response = get(url)
        download_file.write(response.content)


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
