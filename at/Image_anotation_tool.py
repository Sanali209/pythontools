import os
import shutil
import uuid
import hashlib
from PIL import Image

from SLM.appGlue.iotools.pathtools import get_files
from ipywidgets import widgets
from IPython.display import display
#import tqdm
from tqdm.notebook import tqdm

class ItemAnotation:
    def __init__(self) -> None:
        self.label = ""

class ImageItem:

    def __init__(self) -> None:
        self.id = uuid.uuid1()
        self.passed = False
        self.path = ""
        self.contentMD5 = ""
        self.anotation:ItemAnotation = None
        self.note = ""
    
    def CalculateContentMD5(self):
        # load image by pilow
        # calculate md5
        image = Image.open(self.path)
        self.contentMD5  = hashlib.md5(image.tobytes())
        
class AnotationJob:
    def __init__(self) -> None:
        self.name = ""
        self.jsonName = "job.json"
        self.repoPath = ""
        self.cursor = 0
        self.items = []
        self.AnotationChoices = []
        
    def CreateJob(self,name,repoPath,sourcePath,choises:list[str]):
        self.name = name
        self.repoPath = repoPath
        if not os.path.exists(repoPath):
            os.mkdir(repoPath)
        self.AnotationChoices.clear()
        for choise_name in choises:
            self.AnotationChoices.append(ItemAnotation(choise_name))
            
        file_paths = get_files(sourcePath),["*.jpg","*.png","*.jpeg"]
        imageprefix = "image"
        counter = 0
        for file_path in tqdm(file_paths):
            
            item = ImageItem()
            item.path = file_path
            item.CalculateContentMD5()
            self.items.append(item)
            #move file to repoPath
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1]
            path = os.path.join(repoPath,imageprefix+str(counter)+ext)
            # copy file from source to repo
            shutil.copyfile(file_path,path)
            item.path = path
            counter += 1
        #save job
        self.Save()
            
    def Save(self):
        #save to json file located in repoPath
        jsonPath = os.path.join(self.repoPath,self.jsonName)
        jsondata = {}
        jsondata["name"] = self.name
        jsondata["cursor"] = self.cursor
        jsondata['note']=self.note
        for item in self.items:
            jsondata["items"].append({"id":str(item.id),"path":item.path,"contentMD5":item.contentMD5,"anotation":item.anotation.label,"note":item.note})
        jsondata["AnotationChoices"] = []
        for choise in self.AnotationChoices:
            jsondata["AnotationChoices"].append({"label":choise.label})
        with open(jsonPath,"w",encoding="utf-8") as f:
            json.dump(jsondata,f,indent=4)
            
    def Load(self):
        #load from json file located in repoPath
        jsonPath = os.path.join(self.repoPath,self.jsonName)
        with open(jsonPath,"r",encoding="utf-8") as f:
            jsondata = json.load(f)
            self.name = jsondata["name"]
            self.cursor = jsondata["cursor"]
            self.items.clear()
            for item in jsondata["items"]:
                imageitem = ImageItem()
                imageitem.id = uuid.UUID(item["id"])
                imageitem.path = item["path"]
                imageitem.contentMD5 = item["contentMD5"]
                imageitem.anotation = item["anotation"]
                imageitem.note = item["note"]
                self.items.append(imageitem)
            self.AnotationChoices.clear()
            for choise in jsondata["AnotationChoices"]:
                itemAnotation = ItemAnotation()
                itemAnotation.label = choise["label"]
                self.AnotationChoices.append(itemAnotation)
            
    def seek_to_not_anoated(self):
        #seek to first not anoated item
        for item in self.items:
            if item.anotation == None and item.passed == False:
                self.cursor = self.items.index(item)
                return True
            
    def Next(self):
        #seek to next item
        if self.cursor < len(self.items):
            self.cursor += 1
            return True
        else:
            return False
        
    def Previous(self):
        #seek to previous item
        if self.cursor > 0:
            self.cursor -= 1
            return True
        else:
            return False
        
    def Pass(self):
        #pass current item
        self.items[self.cursor].passed = True
        self.Next()
        
        
class JupiterAppGui:
    def __init__(self) -> None:
        self.job = AnotationJob()
        self.repoPath = ""
        
    
    def Inithialize(self):
        self.job.Load()
        self.job.seek_to_not_anoated()
        #horizontal layout
        self.hlayout = widgets.HBox()
        # vertical layout
        self.vlayout = widgets.VBox()
        # image widget
        self.image = widgets.Image()
        self.vlayout.children.append(self.image)
        # anotation widget
        self.anotation = widgets.Dropdown(options=[choise.label for choise in self.job.AnotationChoices])
        self.vlayout.children.append(self.anotation)
        self.noteWidget = widgets.Textarea()
        self.hlayout.children.append(self.vlayout)
        self.hlayout.children.append(self.noteWidget)
        # vertical layout
        self.vlayout2 = widgets.VBox()
        # previous button
        self.previous = widgets.Button(description="Previous")
        self.previous.on_click(self.previous_clicked)
        self.vlayout2.children.append(self.previous)
        # next button
        self.next = widgets.Button(description="Next")
        self.next.on_click(self.next_clicked)
        self.vlayout2.children.append(self.next)
        # pass button
        self.passed = widgets.Button(description="Pass")
        self.passed.on_click(self.passed_clicked)
        self.vlayout2.children.append(self.passed)
        # save button
        self.save = widgets.Button(description="Save")
        self.save.on_click(self.save_clicked)
        self.vlayout2.children.append(self.save)
        self.hlayout.children.append(self.vlayout2)
        self.hlayout.children.append(self.vlayout)
        
    
    def run(self):
        # run gui
        # -----------------------------------
        # image | anotation as list of choises
        #       | note
        # -----------------------------------
        # previous | next | pass| save
        # -----------------------------------
        self.update()
        display(self.hlayout)
        
    def update(self):
        # update gui
        # set image
        self.image.value = open(self.job.items[self.job.cursor].path,"rb").read()
        # set anotation
        self.anotation.value = self.job.items[self.job.cursor].anotation.label
        
    def update_entered_anoation(self):
        # update anotation
        self.job.items[self.job.cursor].anotation.label = self.anotation.value
        
    
    def previous_clicked(self,b):
        self.update_entered_anoation()
        self.job.Previous()
        self.update()
        
    def next_clicked(self,b):
        self.update_entered_anoation()
        self.job.Next()
        self.update()
        
    def passed_clicked(self,b):
        self.job.Pass()
        self.update()
        
    def save_clicked(self,b):
        self.update_entered_anoation()
        self.job.Save()        
        
    