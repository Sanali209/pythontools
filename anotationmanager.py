import os

from transformers import pipeline


# function for get all images from folder recursively
def getImagesFromFolder(folder):
    images = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png"):
                images.append(os.path.join(root, file))
    return images


class AnotationManager:
    def __init__(self) -> None:
        self.anotationJobs = []

    def addAnotationJob(self, anotationJob):
        self.anotationJobs.append(anotationJob)

    def removeAnotationJob(self, anotationJob):
        self.anotationJobs.remove(anotationJob)


class AnotationClass:
    def __init__(self) -> None:
        self.label = ""

    def __repr__(self):
        return self.label

    def __str__(self):
        return self.label


class AnotationJob:
    def __init__(self) -> None:
        self.name = ""
        self.jobfolder = "/rawdb/AJobs/quality"
        self.anotationclassSaveFile = "anotationclass.json"
        self.anotationItemsSaveFile = "anotationitems.json"
        self.transformerPipelineName = "image-classification"
        self.transformerPipeline = pipeline(self.transformerPipelineName)

        self.importPath = ""
        self.exportPath = ""
        self.anotations = []
        self.anotationItems = []

    def ImportAnotationsFromGoolgeDrive(self):
        images = getImagesFromFolder(self.importPath)
        for image in images:
            anotationItem = AnotationItem()
            anotationItem.path = image
            self.anotationItems.append(anotationItem)

    def addAnotation(self, aname):
        nanotation = AnotationClass()
        nanotation.label = aname
        self.anotations.append(nanotation)

    def saveAnotationsClasses(self):
        JsonList = {}
        for cannot in self.anotations:
            JsonList[cannot.label] = cannot.label

        import json
        with open(self.jobfolder + "/" + self.anotationclassSaveFile, 'w') as outfile:
            json.dump(JsonList, outfile, indent=4)

    def loadAnotationsClasses(self):
        import json
        if not os.path.exists(self.jobfolder + "/" + self.anotationclassSaveFile):
            return
        with open(self.jobfolder + "/" + self.anotationclassSaveFile) as json_file:
            data = json.load(json_file)
            for cannot in data:
                nanotation = AnotationClass()
                nanotation.label = cannot
                self.anotations.append(nanotation)

    def saveAnotationsItems(self):
        JsonList = {}
        for cannot in self.anotationItems:
            JsonList[cannot.path] = cannot.path

        import json
        with open(self.jobfolder + "/" + self.anotationItemsSaveFile, 'w') as outfile:
            json.dump(JsonList, outfile, indent=4)

    def loadAnotationsItems(self):
        import json
        if not os.path.exists(self.jobfolder + "/" + self.anotationItemsSaveFile):
            return
        with open(self.jobfolder + "/" + self.anotationItemsSaveFile) as json_file:
            data = json.load(json_file)
            for cannot in data:
                nanotation = AnotationItem()
                nanotation.path = cannot
                self.anotationItems.append(nanotation)
    def NextAnotationItem(self)->'AnotationItem':
        for item in self.anotationItems:
            if not item.anotated and not item.passed:
                return item
        return None


class AnotationItem:
    def __init__(self) -> None:
        self.path = ""
        self.anotations = []
        self.predictions = []
        self.anotated = False
        self.passed = False

    def anotateLabel(self, label):
        self.anotations.append({"label": label})
        self.anotated = True



    def passItem(self):
        self.passed = True



