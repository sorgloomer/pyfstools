_ESCAPING = {
    " ": "\\ ",
    "\t": "\\t",
    "\r": "\\r",
    "\n": "\\n",
    "\\": "\\\\",
}


def escape_filename_char(ch):
    result = _ESCAPING.get(ch, None)
    if result is not None:
        return result
    if ch.isprintable():
        return ch
    return ch.encode('unicode_escape').decode('ascii')


def escape_filename(name):
    return "".join(escape_filename_char(ch) for ch in name)

