
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex

from abc import ABC, abstractmethod
#class Abstract(ABC):
#    @abstractmethod
#    def foo(self):
#        pass

class AbstractGroupItem:

    def __init__(self):
        pass
    
    @abstractmethod
    def toDict(self):
        return None
        
    @abstractmethod
    def getNField(self,n):
        return None
        
    @abstractmethod
    def isItemValid(self):
        return False
    
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
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.items)
        
    def columnCount(self,parent=QModelIndex()):
        return len(self.fields)
            
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        item = self.items[row]
        val = item.getNField(index.column())
        if row < self.rowCount():
            return(QVariant(val))
        else:
            return QVariant()
            
    def addItem(self,item):
        self.items.append(item)