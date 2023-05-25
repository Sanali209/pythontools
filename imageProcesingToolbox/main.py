import shutil

import os

import json
from ipywidgets import widgets
from IPython.display import display, clear_output

from imageProcesingToolbox.enumerations import GroupOptions, ImageOptions, GroupFields, ImageFields


# convert duplicates data format for frendlier use
def convert_dubs_to_json(duplicates):
    dublist = []
    counter = 0
    for key, value in duplicates.items():
        baseimagepath = key
        id = counter
        relatedimages = value
        dupGroup = {GroupFields.id: id, GroupFields.name: id, GroupFields.selected: False,
                    GroupFields.images: [], GroupFields.processingOptions: 'none',
                    GroupFields.optionArgs: 'none'}
        dupGroup[GroupFields.images].append(
            {ImageFields.path: baseimagepath,  ImageFields.selected : False,
             ImageFields.confidence: '1', ImageFields.id: id, ImageFields.processingOptions: 'none',
             ImageFields.optionArgs: 'none'})
        counter += 1
        for relatedimagepath, confidence in relatedimages:
            counter += 1
            id = counter
            dupGroup[GroupFields.images].append(
                {ImageFields.path: relatedimagepath, ImageFields.selected: False,
                 ImageFields.confidence: str(confidence), ImageFields.id: id,
                 ImageFields.processingOptions : 'none', ImageFields.optionArgs: 'none'})
        dublist.append(dupGroup)
        counter += 1
    return dublist


# convert file list for gui drawing
def convertfilelist(listOfFiles):
    filelist = []
    counter = 0
    for filepath in listOfFiles:
        filelist.append({'filepath': filepath, 'selected': False, 'id': counter})
        counter += 1
    return filelist

def save(dublist, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dublist, f, ensure_ascii=False, indent=4)


def loadDubList(path):
    with open(path, 'r', encoding='utf-8') as f:
        dublist = json.load(f)
    return dublist


# don't now need this handler?
def set_selected_group(dublicates, val):
    id = val['owner'].id
    selected = val['new']

    for group in dublicates:
        if group['id'] == id:
            group['selected'] = selected

            break
        for relatedimage in group['relatedimages']:
            if relatedimage['id'] == id:
                relatedimage['selected'] = selected
                break


# Define a function to handle the dropdown value change event
def group_dropdown_changed(change):
    new_value = change['new']
    ovner = change['owner']
    group = ovner.group
    group['groupoptions'] = new_value


# Define a function to handle the group args value change event in text box
def group_args_changed(change):
    new_value = change['new']
    ovner = change['owner']
    group = ovner.group
    group['optionargs'] = new_value
    print(new_value)


# Define a function to handle the dropdown value change event
def image_dropdown_changed(change):
    new_value = change['new']
    ovner = change['owner']
    image = ovner.image
    image['groupoptions'] = new_value


# Define a function to handle the group args value change event in text box
def image_args_changed(change):
    new_value = change['new']
    ovner = change['owner']
    image = ovner.image
    image['optionargs'] = new_value


def draw_images(data, page=1, images_per_page=10):
    # items_layout = widgets.Layout(align_items='center')
    vertical_frame = widgets.VBox()
    # Calculate the start and end index for the current page
    start_index = (page - 1) * images_per_page
    end_index = start_index + images_per_page
    related_images_per_row = 5

    for group in data[start_index:end_index]:
        group_options = GroupOptions.to_list_string()
        image_options = ImageOptions.to_list_string()

        id = group['id']
        related_images = group['relatedimages']
        group_option_value = group['groupoptions']
        group_option_args = group['optionargs']

        # create row of widgets
        row = widgets.HBox()
        # add horizontal group to vertical group
        baseimagegroup = widgets.VBox()

        # create select checkbox
        select_checkbox = widgets.Checkbox(value=group['selected'], description=str(group['id']))
        select_checkbox.id = id
        select_checkbox.observe(lambda value: set_selected_group(data, value), names='value')
        # create label widget
        label_widget = widgets.Label(value=f'ID: {id} Name: {group["name"]}')
        # create dropdown widget
        dropdown_widget = widgets.Dropdown(options=group_options, value=group_option_value,
                                           description='Group options:')
        dropdown_widget.group = group
        dropdown_widget.observe(group_dropdown_changed, names='value')
        # create group args textbox widget
        group_args_widget = widgets.Text(value=group['optionargs'], description='Group args:')
        group_args_widget.group = group
        group_args_widget.observe(group_args_changed, names='value')

        # add widgets to group
        baseimagegroup.children += (select_checkbox, label_widget, dropdown_widget, group_args_widget)

        row.children += (baseimagegroup,)
        rel_counter = 0
        for relatedimage in related_images:
            id = relatedimage['id']
            # create vertical group
            relatedimagegroup = widgets.VBox()
            # create select checkbox
            select_checkbox = widgets.Checkbox(value=relatedimage['selected'], description=str(id))
            select_checkbox.id = id
            select_checkbox.observe(lambda value: set_selected_group(data, value), names='value')

            # create image widget
            relatedimage_widget = widgets.Image(value=open(relatedimage['relatedimagepath'], 'rb').read(), format='jpg',
                                                width=300, heaight=300)
            # create label widget
            filename = relatedimage['relatedimagepath'].split('\\')[-1]
            label_widget = widgets.Label(
                value=f'ID: {relatedimage["id"]} Name: {filename} Conf: {relatedimage["confidence"]}')

            # create dropdown widget
            dropdown_widget = widgets.Dropdown(options=image_options, value=relatedimage['groupoptions'],
                                               description=f'Image options')
            dropdown_widget.image = relatedimage
            dropdown_widget.observe(image_dropdown_changed, names='value')

            # create group args textbox widget
            group_args_widget = widgets.Text(value='', description='Image args:')
            group_args_widget.image = relatedimage
            group_args_widget.observe(image_args_changed, names='value')

            # add widgets to group
            relatedimagegroup.children += (
            select_checkbox, relatedimage_widget, label_widget, dropdown_widget, group_args_widget)

            if rel_counter % related_images_per_row == related_images_per_row - 1:
                # add vertical group to horizontal group
                row.children += (relatedimagegroup,)
                vertical_frame.children += (row,)
                # create new horizontal group
                row = widgets.HBox()
            else:

                # add vertical group to horizontal group
                row.children += (relatedimagegroup,)
            rel_counter += 1

        # Display the related images and labels vertically
        vertical_frame.children += (row,)
    display(vertical_frame)





    # Define button click event handlers
    def process_button_clicked(button):

        # rename groups
        for group in data:
            if group['groupoptions'] == GroupOptions.rename.name:
                RenameGroup(group)
        # merge groups
        for group in data:
            if group['groupoptions'] == GroupOptions.merge.name:
                MergeGroup(group)
        # delete groups
        for group in data:
            if group['groupoptions'] == GroupOptions.del_group_from_list.name:
                del_group_from_list(group)

        # move to folder
        for group in data:
            if group['groupoptions'] == GroupOptions.move_to_folder.name:
                move_to_folder(group)

        # deduplicate images in group
        for group in data:
            if group['groupoptions'] == GroupOptions.deduplicate.name:
                deduplicate_images_in_group(group)

        # delete images from group
        for group in data:
            for image in group['relatedimages']:
                if image['groupoptions'] == ImageOptions.del_from_group.name:
                    image_delete_from_group(image)

        # delete images from list
        for group in data:
            for image in group['relatedimages']:
                if image['groupoptions'] == ImageOptions.del_from_list.name:
                    image_delete_from_list(image)

        #refresh_page()

    def MergeGroup(group):
        merge_to_group = group['optionargs']
        for igroup in data:
            if igroup['name'] == merge_to_group:
                igroup['relatedimages'] += group['relatedimages']
                break
        # delete group from list
        del_group_from_list(group)

    def del_group_from_list(group):
        data.remove(group)

    def deduplicate_images_in_group(group):
        images = group['relatedimages']
        dict_of_images = {}
        for image in images:
            dict_of_images[image['name']] = image

        group['relatedimages'] = list(dict_of_images.values())

    def move_to_folder(group):
        folder = group['optionargs']

        for image in group['relatedimages']:
            filename = image['relatedimagepath'].split('\\')[-1]
            newpath = os.path.join(folder, filename)
            shutil.move(image['relatedimagepath'], newpath)
            image['relatedimagepath'] = newpath

    def RenameGroup(group):
        newname = group['optionargs']
        group['name'] = newname

    # items choises functions
    def image_delete_from_group(image):
        # faind image group
        for group in data:
            if image in group['relatedimages']:
                group['relatedimages'].remove(image)
                break

    def image_delete_from_list(delimage):
        # delete image from list by image path
        for group in data:
            for image in group['relatedimages'].copy():
                if image['relatedimagepath'] == delimage['relatedimagepath']:
                    group['relatedimages'].remove(image)
                    break




# draw all files
def draw_list_images(images_list, page=1, images_per_page=100):
    vertical_frame = widgets.VBox()

    # Calculate the start and end index for the current page
    start_index = (page - 1) * images_per_page
    end_index = start_index + images_per_page
    related_images_per_row = 5

    for image in images_list:
        id = image['id']
        filepath = image['filepath']
        group_option = image['groupoptions']
        option_args = image['optionargs']
        file_name = filepath.split('\\')[-1]
        # create vertical group
        relatedimagegroup = widgets.VBox()
