# def group fields enum
from enum import Enum


class GroupFields(Enum):
    id = 'id'
    name = 'name'
    selected = 'selected'
    images = 'images'
    processingOptions = 'processingOptions'
    optionArgs = 'optionArgs'


class ImageFields(Enum):
    id = 'id'
    path =  'path'
    confidence = 'confidence'
    selected = 'selected'
    groups = 'groups'
    processingOptions =  'processingOptions'
    optionArgs = 'optionArgs'


# Create enemuration for group options
class GroupOptions(Enum):
    none = 0
    rename = 1
    del_group_from_list = 2
    merge = 3
    move_to_folder = 4
    deduplicate = 5

    @staticmethod
    def to_list_string():
        optionstrings = [member.name for member in GroupOptions]
        return optionstrings


# Create enemuration for image options
class ImageOptions(Enum):
    none = 0
    del_from_group = 1
    del_from_list = 2
    del_from_hd = 3
    move_to_group = 4

    @staticmethod
    def to_list_string():
        optionstrings = [member.name for member in ImageOptions]
        return optionstrings
