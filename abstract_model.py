
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, Qt
from .utils import *


from abc import ABC, abstractmethod
#class Abstract(ABC):
#    @abstractmethod
#    def foo(self):
#        pass

class AbstractGroupItem:

    def __init__(self):
        pass
        
    @abstractmethod
    def getNField(self,n):
        return None
        
    @abstractmethod
    def updateNField(self,n,value):
        return None
        
    @abstractmethod
    def checkItem(self):
        return False
        
class ArrayItem(AbstractGroupItem):
    
    def __init__(self,arr):
        self.arr = arr
        self.nb_fields = len(arr)
        
    def getNField(self,n):
        if n < nb_fields:
            return self.arr[n]
        else:
            assert false
            
    def updateNField(self,n,value):
        if n < nb_fields:
            self.arr[n] = value
        else:
            assert false
                 
class DictItem(AbstractGroupItem):
    
    def __init__(self,dict):
        fields = list(dict.keys())
        self.field_to_idx = {f : fields.index(f) for f in fields}
        self.idx_to_fields = {fields.index(f) : f for f in fields}
        self.nb_fields = len(fields)
        self.dict = dict
        
    def getNField(self,n):
        if n < self.nb_fields:
            return self.dict[self.idx_to_fields[n]]
        else:
            assert false
            
    def updateNField(self,n,value):
        if n < self.nb_fields:
            self.dict[self.idx_to_fields[n]] = value
        else:
            assert false
    
class AbstractGroupModel(QAbstractTableModel):

    def __init__(self,parent,fields):
        QAbstractTableModel.__init__(self)
        #super().__init__(self)
        #super().__init__()
        #self.dlg = dlg
        self.fields = fields
        self.nb_fields = len(fields)
        self.items = []
        self.field_of_idx = {f : fields.index(f) for f in fields}
        
    def getNItem(self,n):
        if n < self.rowCount():
            return self.items[n]
        else:
            internal_error("Unexpected index " + str(n))
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.items)
        
    def columnCount(self,parent=QModelIndex()):
        return len(self.fields)
        
    def headerData(self,col,orientation,role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.fields[col])
        return QVariant()
            
    def data(self,index,role):
        debug("data")
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.getNItem(row)
        val = item.getNField(index.column())
        if role != Qt.DisplayRole:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(val))
        else:
            return QVariant()
            
    def setData(self, index, value, role):
        debug("setData")
        if role == Qt.EditRole:
            item = self.getNItem(index.row())
            item.updateNField(index.column(),value)
            self.dataChanged.emit(index, index)
            return True
        return False
            
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            
    def addItem(self,item):
        debug("addItem")
        self.items.append(item)
        self.insertRow(0)
        
    #def dataChanged(self,