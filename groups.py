
from PyQt5.QtSql import QSqlRecord, QSqlTableModel, QSqlField
from PyQt5.QtCore import QVariant, QAbstractTableModel, QModelIndex
from .abstract_model import AbstractGroupModel, AbstractGroupItem, DictItem, DictModel
from .utils import *
         
groups_fields = ["group","descr","layer"]
metagroups_fields = ["metagroup","descr"]
         
class Metagroup(DictItem):
    def __init__(self,metagroup,descr):
        dict = {"metagroup" : metagroup,
                "descr" : descr}
        #assert(metagroups_fields == dict.keys())
        super().__init__(dict)
        
    def checkItem(self):
        pass
         
class GroupItem(DictItem):
    
    def __init__(self,group,descr,layer):
        dict = {"group" : group,
                "descr" : descr,
                "layer" : layer}
        #assert(groups_fields == dict.keys())
        super().__init__(dict)
        
    def checkItem(self):
        pass
        
class GroupModel(DictModel):

    def __init__(self):
        super().__init__(self,groups_fields)
        

class MetagroupModel(DictModel):

    def __init__(self):
        super().__init__(self,metagroups_fields)
        
class Groups:

    def __init__(self,dlg):
        self.dlg = dlg
        self.groupsModel = GroupModel()
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        self.dlg.groupsView.setModel(self.groupsModel)
         
class Metagroups:

    def __init__(self,dlg):
        self.dlg = dlg
        self.metagroupsModel = MetagroupModel()
        
    def initGui(self):
        pass
        
    def connectComponents(self):
        self.dlg.metagroupsView.setModel(self.metagroupsModel)
        self.dlg.metagroupsAdd.clicked.connect(self.addMetagroup)
        self.dlg.metagroupsRemove.clicked.connect(self.removeMetagroup)

    def addMetagroup(self):
        name = self.dlg.metagroupsName.text()
        descr = self.dlg.metagroupsDescr.text()
        metagroupItem = Metagroup(name,descr)
        self.metagroupsModel.addItem(metagroupItem)
        self.metagroupsModel.layoutChanged.emit()
        
    def removeMetagroup(self):
        debug("removeMetagroup")
        indices = self.dlg.metagroupsView.selectedIndexes()
        debug(str(indices))
        self.metagroupsModel.removeItems(indices)
        self.metagroupsModel.layoutChanged.emit()
        #for index in sorted(indices):
        #    debug(str(index.row()))
        #    self.metagroupsModel.removeItem(index)
            #self.metagroupsModel.removeRow(index.row())
        #self.metagroupsModel.layoutChanged.emit()
         
# class GroupItem(AbstractGroupItem):
    
    # def __init__(self,group,descr):
        # self.group = group
        # self.descr = descr
        
    # def getNField(self,n):
        # if n == 0:
            # return self.group
        # elif n == 1:
            # return self.descr
        # else:
            # assert false
            
    # def updateNField(self,n,value):
        # if n == 0:
            # self.group = value
        # elif n == 1:
            # self.descr = value
        # else:
            # assert false
            
    # def checkItem(self):
        # debug("[checkItem] todo")
         
# class GroupModelTest(AbstractGroupModel):

    # def __init__(self,dlg):
        # super().__init__(self,["f1","f2"])
        # self.dlg = dlg
        # self.items = []

# class GroupsModelSql(QSqlTableModel):

    # def __init__(self,dlg):
        # QSqlTableModel.__init__(self)
        # self.dlg = dlg
        
    # def addGroup(self,group):
        # row=self.rowCount()
        # self.insertRecord(0,group)
        # self.setData(self.index(row,0),"test")
        
# class GroupsModel(QAbstractTableModel):

    # def __init__(self,dlg):
        # QAbstractTableModel.__init__(self)
        # self.dlg = dlg
        # self.items = [["toto","t1"],["tata","t2"]]
        
    # def rowCount(self,parent=QModelIndex()):
        # return len(self.items)
        
    # def columnCount(self,parent=QModelIndex()):
        # return 2
    
    # def data(self,index,role):
        # if not index.isValid():
            # return QVariant()
        # row = index.row()
        # col = index.column()
        # if row < self.rowCount():
            # return(QVariant(self.items[row][col]))
        # else:
            # assert false
        
# class Group(QSqlRecord):

    # def __init__(self,name):
        # QSqlRecord.__init__(self)
        # nameField = QSqlField(fieldName="name",type=QVariant.String)
        # self.append(nameField)
        # self.setValue("name",name)
        