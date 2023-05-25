import os
import fnmatch


def get_files(path, exts=None, file_ignore_masck=""):
    if exts is None:
        exts = ["*"]

    matches = []
    for root, dirnames, filenames in os.walk(path):
        for file in filenames:
            if fnmatch.fnmatch(file, file_ignore_masck):
                continue
            for ext in exts:
                # no case match
                if fnmatch.fnmatch(file, ext):
                    matches.append(os.path.join(root, file))
    return matches