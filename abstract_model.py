
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
        
    @abstractmethod
    def equals(self,other):
        return False
        
    @abstractmethod
    def applyItem(self):
        pass
        
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
            
    def equals(self,other):
        self.arr == other.arr
                 
# Dictionary item
# Fields not displayed must be stored at the end
class DictItem(AbstractGroupItem):
    
    def __init__(self,dict,fields=None):
        if not fields:
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
            
    def equals(self,other):
        self.dict == other.dict
        
    def toXML(self):
        xmlStr = "<" + self.__class__.__name__
        for k,v in self.dict.items():
            xmlStr += " " + k + "=\"" + str(v) + "\""
        xmlStr += "/>"
        return xmlStr
    
class AbstractGroupModel(QAbstractTableModel):

    def __init__(self,parent,fields):
        QAbstractTableModel.__init__(self)
        #super().__init__(self)
        #super().__init__()
        #self.dlg = dlg
        self.fields = fields
        #self.nb_fields = len(fields)
        self.items = []
        #self.field_of_idx = {f : fields.index(f) for f in fields}
        
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
        #debug("data")
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
        for i in self.items:
            if i.equals(item):
                warn("Item " + str(item) + " already exists")
                return
        self.items.append(item)
        self.insertRow(0)
        self.layoutChanged.emit()
        
    def removeItems(self,indexes):
        n = 0
        rows = sorted([i.row() for i in indexes])
        for row in rows:
            row -= n
            del self.items[row]
            n += 1
        self.layoutChanged.emit()
        #item = self.getNItem(row)
        #for i in self.items:
        #    if i.equals(item):
        #        self.items.remove(i)
        #        return
        #assert(False)
        
    def applyItems(self):
        debug("[applyItems]")
        for i in self.items:
            i.applyItem()
        
class DictModel(AbstractGroupModel):

    def __init__(self,parent,fields):
        AbstractGroupModel.__init__(self,parent,fields)
        
    # def itemEquals(self,i1,i2):
        # for f in self.fields:
            # if not (i1.dict[f] == i2.dict[f]):
                # debug("diff " + str(i1.dict[f]) + " - " +  str(i2.dict[f]))
                # return False
        # return True
        
    def itemExists(self,item):
        for i in self.items:
            #if self.itemEquals(i,item):
            if i.equals(item):
                return True
        return False
        
    def addItem(self,item):
        debug("DictItem.addItem")
        if self.itemExists(item):
            warn("Item " + str(item) + " already exists")
        else:
            debug("adding item")
            self.items.append(item)
            self.insertRow(0)
        
    def toXML(self):
        xmlStr = " <" + self.__class__.__name__ + ">"
        for i in self.items:
            xmlStr += "  " + i.toXML() + "\n"
        xmlStr += " </" + self.__class__.__name__ + ">"
        return xmlStr
        
        
    #def dataChanged(self,
    
    
    
class AbstractConnector:

    def __init__(self,model,view,addButton,removeButton):
        self.model = model
        self.view = view
        self.addButton = addButton
        self.removeButton = removeButton
        
    def connectComponents(self):
        self.view.setModel(self.model)
        if self.addButton:
            self.addButton.clicked.connect(self.addItem)
        if self.removeButton:
            self.removeButton.clicked.connect(self.removeItem)
        
    @abstractmethod
    def mkItem(self):
        todo_error("mkItem not implemented")
        
    def addItem(self):
        item = self.mkItem()
        self.model.addItem(item)
        self.model.layoutChanged.emit()
        
    def removeItem(self,item):
        indices = self.view.selectedIndexes()
        debug(str(indices))
        self.model.removeItems(indices)
        