
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex, Qt
#from .utils import *
import utils

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
        if n < self.nb_fields:
            return self.arr[n]
        else:
            utils.internal_error("getNField(" + str(n) + ") out of bounds : " + str(nb_fields))
            #assert false
            
    def updateNField(self,n,value):
        if n < self.nb_fields:
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
        
    def recompute(self):
        fields = list(self.dict.keys())
        self.field_to_idx = {f : fields.index(f) for f in fields}
        self.idx_to_fields = {fields.index(f) : f for f in fields}
        self.nb_fields = len(fields)
        
    def getNField(self,n):
        if n < self.nb_fields:
            return self.dict[self.idx_to_fields[n]]
        else:
            utils.debug("getNField " + str(n))
            utils.debug("item fields = " + str(self.dict.keys()))
            utils.internal_error("Accessing " + str(n) + " field < " + str(self.nb_fields))
            
    def updateNField(self,n,value):
        if n < self.nb_fields:
            self.dict[self.idx_to_fields[n]] = value
        else:
            assert false
            
    def equals(self,other):
        return (self.dict == other.dict)
        
    def toXML(self,indent=""):
        xmlStr = indent + "<" + self.__class__.__name__
        for k,v in self.dict.items():
            utils.debug(str(v))
            xmlStr += indent + " " + k + "='" + str(v) + "'"
        xmlStr += "/>"
        return xmlStr
    
class FieldsModel(QAbstractTableModel):

    def __init__(self,parent,dict):
        QAbstractTableModel.__init__(self)
        self.dict = dict
        self.fields = dict.keys()
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.fields)
        
    def columnCount(self,parent=QModelIndex()):
        return 1
    
    def getNItem(self,n):
        return self.dict[self.fields[n]]
    
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.getNItem(row)
        if role != Qt.DisplayRole:
            return QVariant()
        elif row < self.rowCount():
            return(QVariant(item))
        else:
            return QVariant()
            
    def headerData(self,col,orientation,role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant("value")
        elif orientation == Qt.Vertical and role == Qt.DisplayRole:
            return(self.fields[col])
        return QVariant()
    
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
            utils.internal_error("Unexpected index " + str(n))
        
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
        utils.debug("setData")
        if role == Qt.EditRole:
            item = self.getNItem(index.row())
            item.updateNField(index.column(),value)
            self.dataChanged.emit(index, index)
            return True
        return False
            
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
            
    def addItem(self,item):
        utils.debug("addItem")
        for i in self.items:
            if i.equals(item):
                warn("Item " + str(item) + " already exists")
                return
        self.items.append(item)
        self.insertRow(0)
        self.layoutChanged.emit()
        
    def removeField(self,fieldname):
        self.fields.remove(fieldname)
        
    def removeItems(self,indexes):
        utils.debug("[removeItems] nb of items = " + str(len(self.items))) 
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
        utils.debug("[applyItems]")
        for i in self.items:
            i.applyItem()
            
    def orderItems(self,idx):
        utils.debug("orderItems " + str(idx))
        self.items = sorted(self.items, key=lambda i: i.dict[i.idx_to_fields[idx]])
        self.layoutChanged.emit()
        
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
        utils.debug("DictItem.addItem")
        if not item:
            utils.internal_error("Empty item")
        item.checkItem()
        if self.itemExists(item):
            utils.warn("Item " + str(item) + " already exists")
        else:
            utils.debug("adding item")
            self.items.append(item)
            self.insertRow(0)
            
    def removeField(self,fieldname):
        utils.debug("removeField " + fieldname)
        for i in self.items:
            utils.debug(str(i.dict.items()))
            del i.dict[fieldname]
            i.recompute()
        self.fields.remove(fieldname)
        self.layoutChanged.emit()
        
        
    def toXML(self,indent=" "):
        utils.debug("toXML " + self.__class__.__name__)
        xmlStr = indent + "<" + self.__class__.__name__ + ">\n"
        for i in self.items:
            xmlStr += i.toXML(indent=indent + " ") + "\n"
        xmlStr += indent + "</" + self.__class__.__name__ + ">"
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
            self.removeButton.clicked.connect(self.removeItems)
        self.view.horizontalHeader().sectionClicked.connect(self.model.orderItems)
        
    @abstractmethod
    def mkItem(self):
        utils.todo_error("mkItem not implemented")
        
    def addItem(self):
        item = self.mkItem()
        self.model.addItem(item)
        self.model.layoutChanged.emit()
        
    def removeItems(self):
        indices = self.view.selectedIndexes()
        utils.debug(str(indices))
        self.model.removeItems(indices)
        