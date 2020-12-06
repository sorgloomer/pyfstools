pyfstools
=========

A command line tool to pretty print or deep hash directories. Can be used with
any PyFilesystem2 url.

Usage:

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
