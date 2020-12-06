import click

from pyfstools.cmds import cmd_hash, DEFAULT_LS, DEFAULT_FS_URL, cmd_tree, cmd_fstree
from pyfstools.tools import DEFAULT_ALGO
from pyfstools.utils import compose_decorators


@click.group()
def cli():
    pass


def _with_stats():
    return click.option(
        "--no-stats",
        is_flag=True,
        help="""
            Print the number of shown files and directories.
        """,
    )


def _with_path_and_fsurl():
    return compose_decorators(
        click.argument(
            "path",
            type=str,
            default=".",
        ),
        click.option(
            "-U", "--fs-url",
            type=str,
            default=DEFAULT_FS_URL,
            help="""
            Optional PyFilesystem2 fs_url. This is usually parsed from the PATH parameter, but can be supplied
            directly if the inference logic fails or is just undesired.
            \b
            Examples:
                osfs:///
                gs://bucket_name
        """,
        ),
    )


def _command_with_base_tool_args(help):
    return compose_decorators(
        cli.command(help=help + """

            The PATH parameter can include PyFilesystem2 protocol.

            \b
            Examples for the PATH parameter:
                .
                relative_dir/subdir
                /absolute/path
                osfs://relative_dir
                osfs:///absolute_dir
                gs://bucket_name/path/to/dir
        """),
        _with_path_and_fsurl(),
        click.option(
            "-A", "--algo",
            type=str,
            default=DEFAULT_ALGO,
            help="""
                Hash algorithm to he used. Examples: md5, sha1, sha256, sha512. This argument is directly passed to
                Pythons hashlib.new, so it is possible to use system-dependent algorithms as well.
            """,
        ),
        click.option(
            "-e", "--exclude",
            type=str,
            multiple=True,
            help="""Blacklist pattern for files""",
        ),
        click.option(
            "-i", "--include",
            type=str,
            multiple=True,
            help="""Whitelist pattern for files""",
        )
    )


@_command_with_base_tool_args(help="""
    Prints a hash of a given PATH.

    \b
    Examples:
        pyfshash hash
        pyfshash hash /absolute/path
        pyfshash hash --ls
        pyfshash hash --ls -e ".*"
""")
@click.option(
    "-L", "--ls",
    is_flag=True,
    default=DEFAULT_LS,
    help="""
        Print the contents of a directory node. PATH must point to a directory. Note that the printed content is close
        to the bytes that are used for hashing, but might slightly differ. On Windows the line endings in stdout might
        be changed to \\r\\n. When pyfstools hashes a directory internally, it always uses \\n, regardless of platform.
    """,
)
def hash(path, fs_url, ls, algo, exclude, include):
    cmd_hash(
        path=path,
        fs_url=fs_url,
        ls=ls,
        algo=algo,
        excludes=exclude,
        includes=include,
    )


@_command_with_base_tool_args("""
    Prints the directory structure similar to the unix `tree` command.

    \b
    Examples:
        pyfshash tree
        pyfshash tree dir1/dir2
        pyfshash tree -f "{type:.1} {hash:.6} {size:>10} {name}" -e "**/.*" -e ".*" -e "**/__pycache__"
""")
@click.option(
    "-d", "--max-depth",
    type=int,
    default=None,
    help="""
        Maximum depth to print. This option does not affect the hashing algorithm.
    """,
)
@click.option(
    "-f", "--format",
    type=str,
    default=None,
    help="""
        A python format string for nodes.
        \b
        Allowed variables
            `{size}` formatted file size
            `{bsize}` file size in bytes
            `{name}` escaped filename
            `{type}` dir or file
            `{hash}` hash of the node
        \b
        Examples:
            `{name}`
            `{type:.1} {hash:.6} {size:>10} {name}`
    """,
)
@_with_stats()
def tree(path, fs_url, algo, exclude, include, max_depth, format, no_stats):
    cmd_tree(
        path=path,
        fs_url=fs_url,
        algo=algo,
        excludes=exclude,
        includes=include,
        max_depth=max_depth,
        format=format,
        print_stats=not no_stats,
    )


@cli.command(help="""
    Prints the directory structure using PyFilesystem's `fs.tree.render` method.
""")
@_with_path_and_fsurl()
@_with_stats()
def fstree(path, fs_url, no_stats):
    cmd_fstree(
        path=path,
        fs_url=fs_url,
        stats=not no_stats,
    )
