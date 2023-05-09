from pydrive.auth import GoogleAuth

class AnotationManager:
    def __init__(self) -> None:
        self.anotationJobs=[]


    def addAnotationJob(self,anotationJob):
        self.anotationJobs.append(anotationJob)

    def removeAnotationJob(self,anotationJob):
        self.anotationJobs.remove(anotationJob)



class AnotationJob:
    def __init__(self) -> None:
        self.name=""
        self.importPath=""
        self.exportPath=""
        self.anotations=[]
        self.anotationItems=[]

    def ImportAnotationsFromGoolgeDrive(self):
        pass



class Anotation:
    def __init__(self) -> None:
        self.label=""

class AnotationItem:
    def __init__(self) -> None:
        self.path=""
        self.anotations=[]