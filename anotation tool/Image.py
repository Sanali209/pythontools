import uuid
import hashlib
from PIL import Image

class ImageItem:


    def __init__(self) -> None:
        self.id = uuid.uuid1()
        self.path = ""
        self.contentMD5 = ""
    
    def CalculateContentMD5(self):
        # load image by pilow
        # calculate md5
        image = Image.open(self.path)
        self.contentMD5  = hashlib.md5(image.tobytes())

        
    