from ipywidgets import widgets
from IPython.display import display, clear_output

from imageProcesingToolbox.enumerations import GroupOptions, GroupFields


class dubGui:

    def __init__(self, data):

        self.dublist_data = data
        self.groups_per_page = 10
        self.images_per_row = 5
        self.current_page = 1
        self.total_pages = (len(self.dublist_data) + self.groups_per_page - 1) // self.groups_per_page
        self.start_index = (self.current_page - 1) * self.groups_per_page
        self.end_index = self.start_index + self.groups_per_page

        self.rootWidget = widgets.VBox()
        self.paginationWidget = None

    def refreshGui(self):
        clear_output()
        self.total_pages = (len(self.dublist_data) + self.groups_per_page - 1) // self.groups_per_page
        self.start_index = (self.current_page - 1) * self.groups_per_page
        self.end_index = self.start_index + self.groups_per_page
        self.draw()

    def draw(self):
        self.setLayout()
        display(self.rootWidget)

    def processDubs(self):
        pass

    def SetGroupLayout(self, group):
        id = group[GroupFields.id]
        name = group[GroupFields.name]
        group_options = GroupOptions.to_list_string()
        groupWidget = widgets.VBox()
        label = widgets.Label(value=f'Group: {name} ({id})')

        groupWidget.children = [label]
        self.rootWidget.children += (groupWidget)

    def setLayout(self):
        for group in self.dublist_data[self.start_index:self.end_index]:
            self.SetGroupLayout(group)

        # pagination control
        def prevButtonClicked(b):
            if self.current_page > 1:
                self.current_page -= 1
                self.refreshGui()

        def nextButtonClicked(b):
            if self.current_page < self.total_pages:
                self.current_page += 1
                self.refreshGui()

        self.paginationWidget = widgets.HBox()
        prevButton = widgets.Button(description='Prev')
        prevButton.on_click(prevButtonClicked)
        nextButton = widgets.Button(description='Next')
        nextButton.on_click(nextButtonClicked)
        pageLabel = widgets.Label(value=f'Page {self.current_page} of {self.total_pages}')
        processButton = widgets.Button(description='Process dubs')
        processButton.on_click(self.processDubs)
        self.paginationWidget.children = [prevButton, pageLabel, nextButton]
        display(self.paginationWidget)
