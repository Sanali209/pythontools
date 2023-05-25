import streamlit as st
from PIL import Image

from anotationmanager import AnotationJob
from dubFileHelper import DuplicateFindHelper


class StaticContext:
    def __init__(self):
        self.currentJob = AnotationJob()
        self.currentJob.jobfolder = r"G:\Мой диск\rawdb\AJobs\quality"
        self.currentJob.importPath = r"G:\Мой диск\rawdb\image genrs\quality"
        self.currentJob.loadAnotationsClasses()
        self.currentJob.loadAnotationsItems()
        self.dubfainder = DuplicateFindHelper()
        listofimages = [ai.path for ai in self.currentJob.anotations]
        self.dubfainder.RefreshIndex(listofimages)


@st.cache_resource
def get_static_context():
    return StaticContext()



def main():
    context = get_static_context()

    newcat = st.sidebar.text_input("label", "newcat")
    # add new cat
    if st.sidebar.button("Add"):
        context.currentJob.addAnotation(newcat)

    st.sidebar.write(context.currentJob.anotations)

    if st.sidebar.button("Import"):
        context.currentJob.ImportAnotationsFromGoolgeDrive()

    if st.sidebar.button("Save"):
        context.currentJob.saveAnotationsItems()
        context.currentJob.saveAnotationsClasses()

    curent_item = context.currentJob.NextAnotationItem()
    if curent_item is None:
        st.write("No more items")
        return

    #load images
    st.write(curent_item.path)
    image = Image.open(curent_item.path)
    st.image(image, caption=curent_item.path, use_column_width=True)

    # multi select
    selected = st.multiselect('Select', [ai.label for ai in context.currentJob.anotations])

    columns = st.columns(2)
    #pass button
    if columns[0].button("Pass"):
        curent_item.passItem()

    #anotate button
    if columns[1].button("Anotate"):
        curent_item.anotateLabel(selected)
        context.currentJob.saveAnotationsItems()
        context.currentJob.saveAnotationsClasses()












if __name__ == "__main__":
    main()
