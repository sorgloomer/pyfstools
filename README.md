pyfstools
=========

A command line tool to pretty print or deep hash directories. Can be used with
any PyFilesystem2 url.


Installation
------------

    pip install git+https://github.com/sorgloomer/pyfstools.git@main


Usage:
-----

To get a deep-hash of a directory:

    $ python -m pyfstools hash path/to/your/directory
    dir 47393a0d694e987a795272651501c92e3ac3aa4fc7c66ccad6f3e91e858eec43

Note the node type in the first column. It is possible to craft a file that has
the same hash as a given directory. The node type is always included when
calculating directory hashes, so crafting a directory. You should always check
this node type too when checking for subtree equality.


Directories are represented by their contents, their hash is calculated from
this representation:

    $ python -m pyfstools hash --ls path/to/your/directory
    dir  0348bd69ad78babf85960500f5482cfc6f52d7215c5b094c20bed33a17628033 pyfstools
    dir  10b71281b7621f8c5fee7b2f2943bd6bd6cf619e5558f394b4a58851b3cd56c2 test
    file 4733f5c19497f6e3b2a4d88572cbdd6af09cefd0ab42c01e51db11a14830298c .editorconfig
    file ac308f953975bcda2f371c08c7e4643a9fa9ab34ea9627b5812ff7289bf83db1 .gitignore


You can make it easier to spot the differences between two directories by
printing the tree:

    $ python -m pyfstools tree --format "{type:.1} {hash:.8} {name}" test
    d fa587f4b test
    └── d f727fc3d data
        ├── d 6b59393e dir1
        |   └── d cede3ad5 dir2
        |       └── f e3b0c442 text1.txt
        └── f e3b0c442 text2.txt

    3 directories, 2 files


Command Line Documentation
--------------------------

```
$ python -m pyfstools
Usage: __main__.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  fstree  Prints the directory structure using PyFilesystem's...
  hash    Prints a hash of a given PATH.
  tree    Prints the directory structure similar to the unix `tree` command.

Tamas@EFREET MINGW64 /c/workspace/personal/pyfstools (main)
$ python -m pyfstools hash --help
Usage: __main__.py hash [OPTIONS] [PATH]

  Prints a hash of a given PATH.

  Examples:
      pyfshash hash
      pyfshash hash /absolute/path
      pyfshash hash --ls
      pyfshash hash --ls -e ".*"

          The PATH parameter can include PyFilesystem2 protocol.

                  Examples for the PATH parameter:
                      .
                      relative_dir/subdir
                      /absolute/path
                      osfs://relative_dir
                      osfs:///absolute_dir
                      gs://bucket_name/path/to/dir


Options:
  -U, --fs-url TEXT   Optional PyFilesystem2 fs_url. This is usually parsed
                      from the PATH parameter, but can be supplied
                      directly if
                      the inference logic fails or is just undesired.

                      Examples:
                          osfs:///
                          gs://bucket_name
  -A, --algo TEXT     Hash algorithm to he used. Examples: md5, sha1, sha256,
                      sha512. This argument is directly passed to
                      Pythons
                      hashlib.new, so it is possible to use system-dependent
                      algorithms as well.
  -e, --exclude TEXT  Blacklist pattern for files
  -i, --include TEXT  Whitelist pattern for files
  -L, --ls            Print the contents of a directory node. PATH must point
                      to a directory. Note that the printed content is close
                      to the bytes that are used for hashing, but might
                      slightly differ. On Windows the line endings in stdout
                      might
                      be changed to \r\n. When pyfstools hashes a
                      directory internally, it always uses \n, regardless of
                      platform.
  --help              Show this message and exit.


$ python -m pyfstools tree --help
Usage: __main__.py tree [OPTIONS] [PATH]

  Prints the directory structure similar to the unix `tree` command.

  Examples:
      pyfshash tree
      pyfshash tree dir1/dir2
      pyfshash tree -f "{type:.1} {hash:.6} {size:>10} {name}" -e "**/.*" -e ".*" -e "**/__pycache__"

          The PATH parameter can include PyFilesystem2 protocol.

                  Examples for the PATH parameter:
                      .
                      relative_dir/subdir
                      /absolute/path
                      osfs://relative_dir
                      osfs:///absolute_dir
                      gs://bucket_name/path/to/dir


Options:
  -U, --fs-url TEXT        Optional PyFilesystem2 fs_url. This is usually
                           parsed from the PATH parameter, but can be supplied
                           directly if the inference logic fails or is just
                           undesired.

                           Examples:
                               osfs:///
                           gs://bucket_name
  -A, --algo TEXT          Hash algorithm to he used. Examples: md5, sha1,
                           sha256, sha512. This argument is directly passed to
                           Pythons hashlib.new, so it is possible to use
                           system-dependent algorithms as well.
  -e, --exclude TEXT       Blacklist pattern for files
  -i, --include TEXT       Whitelist pattern for files
  -d, --max-depth INTEGER  Maximum depth to print. This option does not affect
                           the hashing algorithm.
  -f, --format TEXT        A python format string for nodes.

                           Allowed
                           variables
                               `{size}` formatted file size
                           `{bsize}` file size in bytes
                               `{name}` escaped
                           filename
                               `{type}` dir or file
                               `{hash}` hash
                           of the node

                           Examples:
                               `{name}`
                               `{type:.1}
                           {hash:.6} {size:>10} {name}`
  --no-stats               Print the number of shown files and directories.
  --help                   Show this message and exit.


$ python -m pyfstools fstree --help
Usage: __main__.py fstree [OPTIONS] [PATH]

  Prints the directory structure using PyFilesystem's `fs.tree.render`
  method.

Options:
  -U, --fs-url TEXT  Optional PyFilesystem2 fs_url. This is usually parsed
                     from the PATH parameter, but can be supplied
                     directly if
                     the inference logic fails or is just undesired.

                     Examples:
                         osfs:///
                         gs://bucket_name
  --no-stats         Print the number of shown files and directories.
  --help             Show this message and exit.
```
