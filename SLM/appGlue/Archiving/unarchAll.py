# get all archives files in a folder and extract them
# pip install patool
# source: https://wummel.github.io/patool/

import os

import patoolib


from SLM.FuncModule import get_files


def unarchAll(folder):
    for file in get_files(folder, ['*.zip', '*.rar','*.7z']):
        root = os.path.dirname(file)
        patoolib.extract_archive(file, outdir=root)


if __name__ == '__main__':
    unarchAll(r'E:\animation\arhives\Julius Zimmerman 2')