from PyQt6.QtWidgets import QTreeWidgetItem

class TreeItem(QTreeWidgetItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.comment = ""
        self.filter_state = 'none'  # 'none', 'filter', 'exclude'
        self.path = ""  # Full path of the item
