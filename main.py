import sys

from decimal import Decimal
from datetime import date
from functools import partial

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from PyQt6 import QtCore
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QStyledItemDelegate,
    QWidget,
    QCalendarWidget,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QDoubleSpinBox,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QPlainTextEdit,
    QSizePolicy,
    QLabel
)

from db_scheme import Base, Department, Professor


engine = create_engine("sqlite:///spravochnik.db")
session_maker = sessionmaker(bind=engine)


class FioDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QLineEdit(parent)
        widget.setMaxLength(60)
        return widget

    def setEditorData(self, editor, index):
        editor.setText(index.data())

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())


class BirthDateDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QCalendarWidget()
        return widget

    def setEditorData(self, editor, index):
        editor.setSelectedDate(QtCore.QDate.fromString(index.data(), "yyyy-MM-dd"))

    def setModelData(self, editor, model, index: QModelIndex):
        model.setData(
            index, date.fromisoformat(editor.selectedDate().toString("yyyy-MM-dd"))
        )


class SocialRatingDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QSpinBox(parent)
        return widget

    def setEditorData(self, editor, index):
        editor.setValue(int(index.data()))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value())


class DepartmentIdDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QComboBox(parent)
        data = (
            index.model()
            .sourceModel()
            .session.execute(select(Department.id, Department.name))
            .all()
        )
        self.id_to_idx = {}
        widget.addItem("None", None)
        self.id_to_idx[None] = 0
        for idx, e in enumerate(data, 1):
            widget.addItem(e[1], e[0])
            self.id_to_idx[e[0]] = idx
        return widget

    def setEditorData(self, editor, index):
        editor.setCurrentIndex(self.id_to_idx[index.data(TableModel.RawRole)])

    def setModelData(self, editor, model, index):
        model.setData(index, editor.itemData(editor.currentIndex()))


class NameDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QLineEdit(parent)
        widget.setMaxLength(100)
        return widget

    def setEditorData(self, editor, index):
        editor.setText(index.data(TableModel.RawRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())


class DescriptionDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        widget = QPlainTextEdit(parent)
        return widget

    def setEditorData(self, editor, index):
        editor.setPlainText(index.data(TableModel.RawRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText())


class BudgetDelegate(QStyledItemDelegate):
    def __init__(self):
        super().__init__(None)

    def createEditor(self, parent, option, index):
        widget = QDoubleSpinBox(parent)
        widget.setDecimals(2)
        widget.setMaximum(1000000)
        return widget

    def setEditorData(self, editor, index):
        editor.setValue(float(index.data()))

    def setModelData(self, editor, model, index):
        model.setData(index, Decimal(editor.text().replace(",", ".")))


COLUMN_NAME_TO_DELEGATE = {
    "professors.fio": FioDelegate,
    "professors.birth_date": BirthDateDelegate,
    "professors.social_rating": SocialRatingDelegate,
    "professors.department_id": DepartmentIdDelegate,
    "departments.name": NameDelegate,
    "departments.description": DescriptionDelegate,
    "departments.budget": BudgetDelegate,
}


class SortModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def lessThan(self, left, right):
        if (self.sourceModel().entity_type == Professor) and (left.column() == 4):
            return left.data() < right.data()
        return left.data(TableModel.RawRole) < right.data(TableModel.RawRole)


class TableModel(QAbstractTableModel):
    RawRole = QtCore.Qt.ItemDataRole.UserRole + 0

    def __init__(self, entity_type):
        super().__init__(None)
        self.entity_type = entity_type
        self.session = session_maker()
        self.table = self.session.query(self.entity_type).all()

    def headerData(self, section, orientation, role):
        if (
            orientation == QtCore.Qt.Orientation.Horizontal
            and role == QtCore.Qt.ItemDataRole.DisplayRole
        ):
            return self.entity_type.__table__.columns.keys()[section]
        return super().headerData(section, orientation, role)

    def rowCount(self, parent):
        return len(self.table)

    def columnCount(self, parent):
        return len(self.entity_type.__table__.columns)

    def data(self, index, role):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if (self.entity_type == Professor) and (index.column() == 4):
                if not self.table[index.row()][index.column()]:
                    return "None"
                return self.session.execute(
                    select(Department.name).where(
                        Department.id == self.table[index.row()][index.column()]
                    )
                ).all()[0][0]
            return str(self.table[index.row()][index.column()])
        elif role == self.RawRole:
            return self.table[index.row()][index.column()]
        return None

    def flags(self, index):
        return QtCore.Qt.ItemFlag.ItemIsEditable | super().flags(index)

    def setData(self, index, value, role):
        self.table[index.row()][index.column()] = value
        return True

    def add_row(self):
        self.beginResetModel()
        self.session.add(self.entity_type())
        self.table = self.session.query(self.entity_type).all()
        self.endResetModel()

    def delete_rows(self, idxes):
        self.beginResetModel()
        for idx in idxes:
            self.session.delete(self.table[idx.row()])
        self.table = self.session.query(self.entity_type).all()
        self.endResetModel()

    def commit(self):
        self.session.commit()

    def revert(self):
        self.beginResetModel()
        self.session.rollback()
        self.table = self.session.query(self.entity_type).all()
        self.endResetModel()

    def close_session(self):
        self.session.close()


class TableViewer(QWidget):
    def __init__(self, entity_type, parent):
        super().__init__(parent)
        self.resize(415, 200)

        self.view = QTableView()
        self.view.setSortingEnabled(True)
        self.model = TableModel(entity_type)
        self.sort_proxy_model = SortModel()
        self.sort_proxy_model.setSourceModel(self.model)
        self.view.setModel(self.sort_proxy_model)

        self.view.resizeColumnsToContents()

        self.delegates = []
        for idx, c in enumerate(entity_type.__table__.columns[1:], 1):
            name = str(c)
            self.delegates.append(COLUMN_NAME_TO_DELEGATE[name]())
            self.view.setItemDelegateForColumn(idx, self.delegates[-1])
        self.view.setColumnHidden(0, True)

        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(self.view, 0, 0, 1, 5)

        add_row_button = QPushButton("Add row")
        add_row_button.clicked.connect(self.model.add_row)
        grid.addWidget(add_row_button, 1, 0)

        delete_rows_button = QPushButton("Delete rows")
        delete_rows_button.clicked.connect(
            lambda: self.model.delete_rows(self.view.selectedIndexes())
        )
        grid.addWidget(delete_rows_button, 1, 1)

        commit_button = QPushButton("Commit")
        commit_button.clicked.connect(self.model.commit)
        grid.addWidget(commit_button, 1, 2)

        revert_button = QPushButton("Revert")
        revert_button.clicked.connect(self.model.revert)
        grid.addWidget(revert_button, 1, 3)

        back_button = QPushButton("Back")
        back_button.clicked.connect(parent.clicked_back_button)
        back_button.clicked.connect(self.model.close_session)
        grid.addWidget(back_button, 1, 4)


class DatabaseViewer(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        label = QLabel("Выберите таблицу")
        layout.addWidget(label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        for name in Base.metadata.tables.keys():
            button = QPushButton(name)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.clicked.connect(
                partial(parent.clicked_table_button, eval(name.capitalize()[:-1]))
            )
            layout.addWidget(button)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("Справочник")
        self.setCentralWidget(DatabaseViewer(self))

    def clicked_table_button(self, entity_type):
        self.setCentralWidget(TableViewer(entity_type, self))

    def clicked_back_button(self):
        self.setCentralWidget(DatabaseViewer(self))


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
