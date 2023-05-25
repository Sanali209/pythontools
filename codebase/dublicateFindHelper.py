import time

from typing import Dict

import numpy as np
from annoy import AnnoyIndex
from imagededup.methods import CNN
from tqdm import tqdm

from codebase.os_path_tools import get_files
from codebase.segmentedFilesHash import SegmentedFilesHash


class DuplicateFindHelper:

    def __init__(self, EncodingHash_Path: str = None):
        self.image_paths = None
        self.AnnoyIndex = None
        self.futuresMap = None
        self.cnn_encoder = CNN(verbose=True)
        if EncodingHash_Path is None:
            self.EncodingHash = SegmentedFilesHash('data/TensorEncodingHash')
        else:
            self.EncodingHash = SegmentedFilesHash(EncodingHash_Path)

    def RefreshIndeksDir(self, dirPath):
        imagePats = get_files(dirPath, ['*.jpg', '*.png', '*.jpeg'])
        self.RefreshIndex(imagePats)

    def RefreshIndex(self, ImagePats: list[str]):
        futuresMap = self.CreateCNNEncoding(ImagePats)
        keylist = list(futuresMap.keys())
        self.image_paths = keylist

        fLen = len(futuresMap[keylist[0]])  # Length of item vector that will be indexed

        t = AnnoyIndex(fLen, 'euclidean')

        for i, v in tqdm(zip(range(len(futuresMap)), futuresMap.values())):
            t.add_item(i, v)

        t.build(100)  # 100 trees

        self.AnnoyIndex = t

    def FindTopSimilar(self, ImagePath: str, TopCount: int) -> list[str]:
        v = self.GetCNNEncoding(ImagePath)
        u = self.AnnoyIndex
        # u.load(config.image_features_vectors_ann)  # super fast, will just mmap the file
        index_list = u.get_nns_by_vector(v, TopCount)  # will find the 10 nearest neighbors

        listSimPats = []
        for i in index_list:
            listSimPats.append(self.image_paths[i])

        return listSimPats

    def CreateCNNEncoding(self, imagePaths: list) -> dict:

        if imagePaths is None:
            raise Exception("imagePaths is None")

        if len(imagePaths) == 0:
            raise Exception("imagePaths is empty")

        encodingMap = {}

        progress = tqdm(imagePaths)
        for path in progress:

            if path in self.EncodingHash:
                value = self.EncodingHash[path]
                encodingMap[path] = self.BinToNPArray(value)
            else:
                ThumbPath = path
                try:
                    future = self.cnn_encoder.encode_image(ThumbPath)
                except Exception as e:
                    print("wrong file: " + path)
                    print(e)
                    # assign tu future blank np.array shape(1,576)
                    future = [np.zeros((256, 1))]
                    continue
                self.EncodingHash[path] = self.NPArrayToBin(future[0])
                encodingMap[path] = future[0]
        return encodingMap

    def GetCNNEncoding(self, imagePath: str) -> np.array:
        if imagePath == None:
            raise Exception("imagePath is None")
        if len(imagePath) == 0:
            raise Exception("imagePath is empty")

        future = self.cnn_encoder.encode_image(imagePath)
        return future[0]

    def FaindCNNDubs(self, encodingMap: Dict[str, list], similarity: float = 0.85, score=True) -> dict:
        """use wiz CreateCNNEncoding
        Sample:
        listOfFiles = get_files(self.ProcesingPath, exts=['*.jpg', '*.png', '*.jpeg'])
        encodingmap = DuplicateFindHelper.CreateCNNEncoding(listOfFiles)
        duplicates = DuplicateFindHelper.FaindCNNDubs(encodingmap, similarity=0.85)
        """

        result = self.cnn_encoder.find_duplicates(image_dir=None, encoding_map=encodingMap,
                                                  min_similarity_threshold=similarity, scores=score)
        return result

    def FaindItemsAsFolder(self, directory, etalondirectory, similarity: float = 0.85) -> dict:

        etalonImages = get_files(etalondirectory, ['*.jpg', '*.jpeg', '*.png', '*.bmp'])
        gallimages = get_files(directory, ['*.jpg', '*.jpeg', '*.png', '*.bmp'])

        return None

    @staticmethod
    def NPArrayToArry(array: np.array) -> list:
        return array.tolist()

    def NPArrayToBin(self, array: np.array) -> bytes:
        return array.tobytes()

    def BinToNPArray(self, array: bytes) -> np.array:
        return np.frombuffer(array, dtype=np.float32)

    @staticmethod
    def ArryToNPArray(array: list) -> np.array:
        return np.array(array)

    @staticmethod
    def ClearEmptyDubsGroup(dubDictionary: dict[str, list]):
        """remove empty dubs group from dictionary"""
        for key in dubDictionary.copy():
            if len(dubDictionary[key]) == 0:
                del dubDictionary[key]

    @staticmethod
    def ClearFullCollidedDubsGroup(dubDictionary: dict[str, list]):
        """remove full collided dubs group from dictionary in place(modify input dictionary)
                return count of removed dubs and time of operation in seconds

                Parameters:
                    dubDictionary : dict[str, list]
                        dictionary of dubs
                    Returns:
                    int : count of removed dubs
                    float : time of operation in seconds

                Sample:
                    | listOfFiles = get_files(self.ProcesingPath, exts=['*.jpg', '*.png', '*.jpeg'])
                    | encodingmap = DuplicateFindHelper.CreateCNNEncoding(listOfFiles)
                    | duplicates = DuplicateFindHelper.FaindCNNDubs(encodingmap, similarity=0.85)
                    | DuplicateFindHelper.ClearFullCollidedDubsGroup(duplicates)
                """
        currentTime = time.time()
        remKeys = set()

        listOfDirKeys = list(dubDictionary.keys())
        tqdmprogress = tqdm(range(len(listOfDirKeys)), total=len(listOfDirKeys), desc="ClearFullCollidedDubsGroup")
        for i in tqdmprogress:
            path1 = listOfDirKeys[i]

            if path1 in remKeys:
                continue

            for j in range(i + 1, len(listOfDirKeys)):

                path2 = listOfDirKeys[j]
                if path2 in remKeys:
                    continue
                items1 = {path1, *[item[0] for item in dubDictionary[path1]]}
                items2 = {path2, *[item[0] for item in dubDictionary[path2]]}
                # if sets equal
                if items1 == items2:
                    remKeys.add(path2)
                    break
                # compare if all items present in list2
                if items2.issubset(items1):
                    remKeys.add(path2)
                    break
                # compare if all items present in list1
                if items1.issubset(items2):
                    remKeys.add(path1)
                    break

        for key in remKeys:
            del dubDictionary[key]
        lastTime = time.time()
        print(f"removed {len(remKeys)} dubs")

        return len(remKeys), lastTime - currentTime