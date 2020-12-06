import fs as pyfs
import fs.tree

from pyfshash.tools import HashTool, TreeTool
from pyfshash.utils import param_open_fs

DEFAULT_LS = False
DEFAULT_FS_URL = None


def open_path(path, fs_url=None):
    if fs_url:
        return pyfs.open_fs(fs_url), path
    if "://" in path:
        fs, root = pyfs.opener.open(path)
        if root is None:
            root = "/"
        return fs, root
    fs = pyfs.open_fs("osfs://")
    if not path:
        path = '.'
    return fs, path


def cmd_hash(
    path, *, fs_url=None, ls=DEFAULT_LS, **kwargs
):
    if ls is None:
        ls = DEFAULT_LS
    fs, path = open_path(path, fs_url)
    tool = HashTool(fs=fs, **kwargs)
    if ls:
        tool.print_path_ls(path)
    else:
        tool.print_path_hash(path)


def cmd_tree(path, *, fs_url=None, **kwargs):
    fs, path = open_path(path, fs_url)
    tool = TreeTool(fs=fs, **kwargs)
    tool.print(path)


def cmd_fstree(path, *, fs_url=None, stats=None, **kwargs):
    fs, path = open_path(path, fs_url)
    if stats is None:
        stats = True
    if path is None:
        path = '/'
    fs = param_open_fs(fs)
    count_dir, count_file = pyfs.tree.render(fs, path, **kwargs)
    if stats:
        print()
        print(f"{count_dir} directories, {count_file} files")
