import binascii
import fnmatch
import hashlib

import fs as pyfs
import fs.filesize

from pyfstools.escape import escape_filename
from pyfstools.utils import param_open_fs, mark_iterable_ends

DEFAULT_ALGO = "sha256"


class ToolBase:
    _namespaces = None

    def __init__(self, fs, *, excludes=None, includes=None):
        self.fs = param_open_fs(fs)
        self.excludes = excludes
        self.includes = includes

    @staticmethod
    def _escape_filename(name):
        return escape_filename(name)

    @staticmethod
    def _type_order(info):
        return 1 if info.is_dir else 2

    def _info_order(self, info):
        return self._type_order(info), info.name

    def _sort_infos(self, infos):
        return sorted(infos, key=self._info_order)

    def _scandir(self, path):
        infos = self.fs.scandir(path, namespaces=self._namespaces)
        infos = self._sort_infos(infos)
        return [info for info in infos if self._included(info.make_path(path), info)]

    def _included(self, path, info):
        if self.excludes:
            for exclude_pattern in self.excludes:
                if fnmatch.fnmatch(path, exclude_pattern):
                    return False
        if not self.includes:
            return True
        for include_pattern in self.includes:
            if fnmatch.fnmatch(path, include_pattern):
                return True
        return False

    def _info(self, path):
        return self.fs.getinfo(path, namespaces=self._namespaces)


class HashTool(ToolBase):
    buffer_size = 1024 ** 2

    def __init__(self, fs, algo=None, **kwargs):
        if algo is None:
            algo = DEFAULT_ALGO
        super().__init__(fs, **kwargs)
        self._algo = algo
        self._cache = dict()

    def print_path_hash(self, path):
        print(self.path_hash(path))

    def print_path_ls(self, path):
        for line in self.path_ls(path):
            print(line)

    def path_hash(self, path):
        info = self._info(path)
        return self._path_hash(path, info)

    def path_ls(self, path):
        info = self._info(path)
        if info.is_dir:
            yield from self.make_tree(path)
        else:
            yield self.path_hash(path)

    def make_tree(self, dir_path):
        infos = self._scandir(dir_path)
        for info in infos:
            yield self.make_line(info.make_path(dir_path), info)

    def make_line(self, path, info):
        hashhex = self._hash_entry(path, info)
        typestr = self._typeof_info(info)
        name = self._escape_filename(info.name)
        return f"{typestr:<4} {hashhex} {name}"

    def _path_hash(self, path, info):
        info_type = self._typeof_info(info)
        info_hash = self._hash_entry(path, info)
        return f"{info_type} {info_hash}"

    @staticmethod
    def _typeof_info(info):
        if info.is_dir:
            return "dir"
        if info.is_file:
            return "file"
        if info.is_link:
            return "link"
        raise NotImplementedError("only files and folders supported")

    @staticmethod
    def _to_hex(my_bytes):
        return binascii.hexlify(my_bytes).decode('ascii')

    def _make_hasher(self):
        return hashlib.new(self._algo)

    def _hash_chunks(self, chunks):
        hasher = self._make_hasher()
        for chunk in chunks:
            hasher.update(chunk)
        hashbytes = hasher.digest()
        return binascii.hexlify(hashbytes).decode('utf-8')

    def _file_chunks(self, stream):
        while True:
            chunk = stream.read(self.buffer_size)
            if not chunk:
                return
            yield chunk

    def _tree_chunks(self, path):
        for line in self.make_tree(path):
            yield f"{line}\n".encode('utf-8')

    def _hash_entry(self, path, info):
        cache = self._cache
        if cache is not None:
            cached = cache.get(path)
            if cached is not None:
                return cached
        result = self._hash_entry_uncached(path, info)
        if cache is not None:
            cache[path] = result
        return result

    def _hash_entry_uncached(self, path, info):
        if info.is_dir:
            return self._hash_tree(path)
        return self._hash_file(path)

    def _hash_tree(self, path):
        return self._hash_chunks(self._tree_chunks(path))

    def _hash_file(self, path):
        with self.fs.open(path, 'rb') as f:
            return self._hash_chunks(self._file_chunks(f))

    def _hash_path_uncached(self, path):
        info = self._info(path)
        return self._hash_entry_uncached(path, info)


class TreeTool(ToolBase):
    _indent_cm = '├── '
    _indent_cl = '└── '
    _indent_sm = '|   '
    _indent_sl = '    '

    def __init__(self, fs, format=None, max_depth=None, algo=None, print_stats=None, dirs_first=None, **kwargs):
        if print_stats is None:
            print_stats = True
        if dirs_first is None:
            dirs_first = True
        if format is None:
            format = "{name}"
        super().__init__(fs, **kwargs)
        self._print_stats = print_stats
        self._dirs_first = dirs_first
        self._format_str = format
        self._max_depth = max_depth
        # checking for "{size" instead of "{size}" to allow things like "{size:1.1}"
        self._collect_size = "{size" in format or "{bsize" in format
        self._collect_hash = "{hash" in format
        self._hasher = None
        if self._collect_hash:
            self._hasher = HashTool(fs=self.fs, algo=algo)
        self._namespaces = ('details',) if self._collect_size else None

    def _type_order(self, info):
        return 1 if self._dirs_first and info.is_dir else 2

    def print(self, path):
        for line in self.tree_lines(path):
            print(line)

    def tree_lines(self, path, stats=None):
        if stats is None:
            stats = TreeStats()
        info = self._info(path)
        yield self._format_entry(path, info, name_overwrite=path)
        yield from self._visit_node(path, info, depth=0, stats=stats)
        if self._print_stats:
            yield ""
            yield f"{stats.count_dir} directories, {stats.count_file} files"

    def _visit_node(self, path, info, depth, stats=None):
        if stats is not None and depth > 0:
            if info.is_file:
                stats.count_file += 1
            if info.is_dir:
                stats.count_dir += 1
        if not info.is_dir:
            return
        if self._max_depth is not None and depth >= self._max_depth:
            return
        for iteration in mark_iterable_ends(self._scandir(path)):
            child_info = iteration.value
            child_path = child_info.make_path(path)
            prefix_c = self._indent_cl if iteration.last else self._indent_cm
            prefix_s = self._indent_sl if iteration.last else self._indent_sm
            formatted = self._format_entry(child_path, child_info)
            yield prefix_c + formatted
            for line in self._visit_node(
                path=child_info.make_path(path),
                info=child_info,
                depth=depth + 1,
                stats=stats
            ):
                yield prefix_s + line

    def _format_entry(self, path, info, name_overwrite=None):
        mytype = self._info_type(info)
        myhash = self._hash(path, info)
        myrawsize = None
        if self._collect_size and not info.is_dir:
            myrawsize = info.size
        mybsize = myrawsize
        if mybsize is None:
            mybsize = '-'
        myfsize = self._format_size(myrawsize)
        myname = info.name if name_overwrite is None else name_overwrite
        return self._format_str.format(
            name=myname,
            path=path,
            type=mytype,
            bsize=mybsize,
            size=myfsize,
            hash=myhash,
        )

    def _info_type(self, info):
        if info.is_dir:
            return "dir"
        if info.is_file:
            return "file"
        if info.is_link:
            return "link"
        return NotImplementedError("unknown info type")

    def _hash(self, path, info):
        hasher = self._hasher
        if hasher is None:
            return None
        return hasher._hash_entry(path, info)

    @staticmethod
    def _format_size(size):
        if size is None:
            return '-'
        return pyfs.filesize.binary(size)


class TreeStats:
    def __init__(self):
        self.count_dir = 0
        self.count_file = 0
