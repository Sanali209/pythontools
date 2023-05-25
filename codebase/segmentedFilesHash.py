import hashlib
import logging
import os
import pickle
from typing import Any


class SegmentedFilesHash(dict[str, Any]):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._filepath = args[0] if len(args) > 0 else kwargs.get("filepath", None)
        if self._filepath is None:
            raise Exception("filepath is not set")
        else:
            if self._filepath.endswith("\\") or self._filepath.endswith("/"):
                self._filepath = self._filepath[:-1]
            if not os.path.exists(self._filepath):
                os.makedirs(self._filepath)
            self._LoadKeys()

    def _SaveKeys(self):
        path = os.path.join(self._filepath, "keys.pk")
        with open(path, "wb") as f:
            pickle.dump(list(self.keys()), f)

    def _LoadKeys(self):
        path = os.path.join(self._filepath, "keys.pk")
        if not os.path.exists(path):
            return
        with open(path, "rb") as f:
            try:
                keys = pickle.load(f)
            except Exception as e:
                logging.log(logging.ERROR, e, exc_info=True, stack_info=True)
                return
        self.update({key: None for key in keys})

    def _SaveItem(self, key, value):
        # konvert key to md5
        md5key = hashlib.md5(key.encode()).hexdigest()
        itempath = os.path.join(self._filepath, md5key)
        with open(itempath, "wb") as f:
            pickle.dump(value, f)

    def _DeleteItem(self, key):
        itempath = os.path.join(self._filepath, key)
        if os.path.exists(itempath):
            os.remove(itempath)

    def _LoadItem(self, key):
        # konvert key to md5
        md5key = hashlib.md5(key.encode()).hexdigest()
        itempath = os.path.join(self._filepath, md5key)
        if not os.path.exists(itempath):
            return False, None
        with open(itempath, "rb") as f:
            try:
                item = pickle.load(f)
            except Exception as e:
                logging.log(logging.ERROR, e, exc_info=True, stack_info=True)
                return False, None
            return True, item

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._SaveItem(key, value)
        self._SaveKeys()

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        item = super().__getitem__(key)
        if item is None:
            loaded, item = self._LoadItem(key)
            if loaded:
                self[key] = item
            else:
                raise KeyError(key)
        return super().__getitem__(key)

    def __delitem__(self, key):
        super().__delitem__(key)
        self._DeleteItem(key)
        self._SaveKeys()