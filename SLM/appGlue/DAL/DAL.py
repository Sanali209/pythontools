


class DataAdapter:
    def __init__(self):
        self.converters = []

    def Convert(self, data_item, target_type):
        for converter in self.converters:
            if converter.sourcetpe == type(data_item) and converter.targettype == target_type:
                return converter.Convert(data_item, )
            if converter.targettype == type(data_item) and converter.sourcetpe == target_type:
                return converter.ConvertBack(data_item)
        return None
class DataSchema:
    def __init__(self):
        self.name = ""
        self.dataclass = None
        self._datasource = None
        self.fields = []


class DataField:
    def __init__(self, name="", field_type: type = str, default=None):
        self.name = name
        self.field_type = field_type
        self.default = default
        self.getCallback = None
        self.setCallback = None

    def GetValue(self):
        if self.getCallback is not None:
            return self.getCallback()

    def SetValue(self, value):
        if self.setCallback is not None:
            self.setCallback(value)


class InterableDataField(DataField):
    def __init__(self, name="", field_type: type = list, default=[]):
        super().__init__(name, field_type, default)

    def __iter__(self):
        return iter(self.GetValue())

    def __len__(self):
        return len(self.GetValue())

    def __getitem__(self, key):
        return self.GetValue()[key]

    def __setitem__(self, key, value):
        self.GetValue()[key] = value

    def __delitem__(self, key):
        del self.GetValue()[key]

    def __contains__(self, item):
        return item in self.GetValue()


class DataSchemeMapper:
    def __init__(self):
        self.schemas = {}

    def CopyData(self, source, target):
        if type(source) in self.schemas:
            source_schema = self.schemas[type(source)]
            target_schema = self.schemas[type(target)]
            for field in source_schema.fields:
                if field.name in target_schema.fields:
                    target_schema.fields[field.name].SetValue(field.GetValue())

    def AddSchema(self, schema):
        self.schemas[schema.dataclass] = schema


class DataProvider:
    def __init__(self):
        self.name = "DataProviderBase"
        self.dataformath = ''
        self.dataAdapter = DataAdapter()

        self.backStores = []

    def GetDataItem(self, **kwargs):
        # abstract method
        return None

    def GetDataItemFormat(self, dataitem):
        pass

    def GetDataItemByByBackStore(self, storename, **kwargs):
        for store in self.backStores:
            if store.name == storename:
                dataitem = store.GetDataItem(**kwargs)
                formath = store.GetDataItemFormat(dataitem)
                return self.dataAdapter.Convert(dataitem, formath)

    def SetDataItem(self, item, **kwargs):
        # abstract metod
        for store in self.backStores:
            store.SetDataItem(item, **kwargs)

    def deleteDataItem(self, item):
        # abstract metod
        for store in self.backStores:
            store.deleteDataItem(item)

    def all(sel, **kwargs):
        return None

    def OnDataChange(self, **kwargs):
        for store in self.backStores:
            store.OnDataChange(**kwargs)

    def InvokeDataChange(self, **kwargs):
        for store in self.backStores:
            store.InvokeDataChange(**kwargs)

    def commit(self):
        for store in self.backStores:
            store.commit()


class DataConverter:

    def Convert(self, data):
        return None

    def ConvertBack(self, data):
        return None
