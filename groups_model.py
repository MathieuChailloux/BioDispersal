
from PyQt5.QtSql import QSqlRecord, QSqlTableModel, QSqlField
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from .abstract_model import AbstractGroupModel, AbstractGroupItem
         
class GroupItem(AbstractGroupItem):
    
    def __init__(self,group,descr):
        self.group = group
        self.descr = descr
        
    def getNField(self,n):
        if n == 0:
            return self.group
        elif n == 1:
            return self.descr
        else:
            assert false
         
class GroupModelTest(AbstractGroupModel):

    def __init__(self,dlg):
        super().__init__(self,["f1","f2"])
        self.dlg = dlg
        self.items = []

class GroupsModelSql(QSqlTableModel):

    def __init__(self,dlg):
        QSqlTableModel.__init__(self)
        self.dlg = dlg
        
    def addGroup(self,group):
        row=self.rowCount()
        self.insertRecord(0,group)
        self.setData(self.index(row,0),"test")
        
class GroupsModel(QAbstractTableModel):

    def __init__(self,dlg):
        QAbstractTableModel.__init__(self)
        self.dlg = dlg
        self.items = [["toto","t1"],["tata","t2"]]
        
    def rowCount(self,parent=QModelIndex()):
        return len(self.items)
        
    def columnCount(self,parent=QModelIndex()):
        return 2
    
    def data(self,index,role):
        if not index.isValid():
            return QVariant()
        row = index.row()
        col = index.column()
        if row < self.rowCount():
            return(QVariant(self.items[row][col]))
        else:
            assert false
        
class Group(QSqlRecord):

    def __init__(self,name):
        QSqlRecord.__init__(self)
        nameField = QSqlField(fieldName="name",type=QVariant.String)
        self.append(nameField)
        self.setValue("name",name)
        