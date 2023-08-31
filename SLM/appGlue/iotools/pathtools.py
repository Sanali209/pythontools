from tqdm import tqdm




class PathManagerSys:
    dir_paths = []
    dir_black_list = []
    file_black_list = []
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tif', '*.tiff']

    def addDirPath(self, path):
        self.dir_paths.append(path)

    def addDirBlackList(self, path):
        self.dir_black_list.append(path)

    def addFileBlackList(self, path):
        self.file_black_list.append(path)

    def getFiles(self):
        files = []
        for dir_path in self.dir_paths:
            files.extend(get_files(dir_path, self.extensions))
        for dir_black in self.dir_black_list:
            files = [file for file in files if dir_black not in file]
        for file_black in self.file_black_list:
            files = [file for file in files if file_black != file]
        return files

    def IsFileInBlackList(self, filepath):
        for dir_black in self.dir_black_list:
            if dir_black in filepath:
                return True
        for file_black in self.file_black_list:
            if file_black == filepath:
                return True
        return False

    def ImportSettingsFromData(self, data):
        self.dir_paths = data.get('dir_paths', [])
        self.dir_black_list = data.get('dir_black_list', [])
        self.file_black_list = data.get('file_black_list', [])
        self.extensions = data.get('extensions', self.extensions)

    def ExportSettingsToData(self):
        data = {'dir_paths': self.dir_paths, 'dir_black_list': self.dir_black_list,
                'file_black_list': self.file_black_list, 'extensions': self.extensions}
        return data

def get_files(path, exts=None, file_ignore_masck=""):
    """
    :param path: ProjectSettingsPath to search
    :param exts: list of extensions to search ["*.jpg", "*.png"] need include "*" in mask
       :param file_ignore_masck:  of files to ignore "Thumbs.db"
    """
    if exts is None:
        exts = ["*"]
    import os
    import fnmatch
    matches = []
    for root, dirnames, filenames in tqdm(os.walk(path)):
        for file in filenames:
            if fnmatch.fnmatch(file, file_ignore_masck):
                continue
            for ext in exts:
                # no case match
                if fnmatch.fnmatch(file, ext):
                    matches.append(os.path.join(root, file))
    return matches