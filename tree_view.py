from PyQt6.QtWidgets import QTreeWidget, QMenu, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from tree_item import TreeItem


class TreeView(QTreeWidget):
    # Signals to communicate with other components
    itemStateChanged = pyqtSignal()
    itemSelected = pyqtSignal(TreeItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Name", "Type"])
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 100)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        self.itemSelectionChanged.connect(self.on_item_selection_changed)

    def populate_tree(self, path):
        """Recursively populate the tree widget with directory contents."""
        self.clear()
        root_item = TreeItem([path.name, "Directory"])
        root_item.comment = ""
        root_item.path = str(path.resolve())
        self.addTopLevelItem(root_item)
        self._populate_tree_recursive(root_item, path)
        root_item.setExpanded(True)

    def _populate_tree_recursive(self, parent_item, path):
        try:
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if item.is_dir():
                    child_item = TreeItem([item.name, "Directory"])
                    child_item.comment = ""
                    child_item.path = str(item.resolve())
                    parent_item.addChild(child_item)
                    self._populate_tree_recursive(child_item, item)
                else:
                    child_item = TreeItem([item.name, "File"])
                    child_item.comment = ""
                    child_item.path = str(item.resolve())
                    parent_item.addChild(child_item)
        except PermissionError:
            child_item = TreeItem(["[Permission Denied]", "Directory"])
            child_item.comment = ""
            child_item.path = ""
            parent_item.addChild(child_item)
        except Exception as e:
            child_item = TreeItem([f"[Error: {str(e)}]", "File"])
            child_item.comment = ""
            child_item.path = ""
            parent_item.addChild(child_item)

    def load_tree_from_json(self, root_json):
        """Recursively populate the tree widget from JSON data."""
        self.clear()
        name = root_json.get('name', '')
        type_ = root_json.get('type', '').capitalize()
        comment = root_json.get('comment', '')
        filter_state = root_json.get('filter_state', 'none')
        path = root_json.get('path', '')

        root_item = TreeItem([name, type_])
        root_item.comment = comment
        root_item.filter_state = filter_state
        root_item.path = path
        self.addTopLevelItem(root_item)
        self._populate_tree_from_json_recursive(root_item, root_json)
        root_item.setExpanded(True)
        self.update_item_appearance(root_item)

    def _populate_tree_from_json_recursive(self, parent_item, node_json):
        contents = node_json.get('contents', [])
        for child in contents:
            name = child.get('name', '')
            type_ = child.get('type', '').capitalize()
            comment = child.get('comment', '')
            filter_state = child.get('filter_state', 'none')
            path = child.get('path', '')
            child_item = TreeItem([name, type_])
            child_item.comment = comment
            child_item.filter_state = filter_state
            child_item.path = path
            parent_item.addChild(child_item)
            if type_.lower() == "directory":
                self._populate_tree_from_json_recursive(child_item, child)

    def build_tree_json(self, item):
        """Recursively build the JSON representation of the tree."""
        node = {
            "name": item.text(0),
            "type": item.text(1).lower(),
            "comment": getattr(item, 'comment', ''),
            "filter_state": getattr(item, 'filter_state', 'none'),
            "path": getattr(item, 'path', '')
        }
        if item.childCount() > 0:
            node["contents"] = []
            for i in range(item.childCount()):
                child = item.child(i)
                node["contents"].append(self.build_tree_json(child))
        return node

    def open_context_menu(self, position):
        """Open a context menu to filter or exclude items."""
        selected_item = self.itemAt(position)
        if selected_item:
            menu = QMenu()
            # Prevent filtering or excluding the root item
            if selected_item != self.topLevelItem(0):
                filter_action = menu.addAction("Filter Item")
                exclude_action = menu.addAction("Exclude Item")
                remove_action = menu.addAction("Remove Filter/Exclude")
                filter_action.triggered.connect(lambda: self.set_item_state(selected_item, 'filter'))
                exclude_action.triggered.connect(lambda: self.set_item_state(selected_item, 'exclude'))
                remove_action.triggered.connect(lambda: self.set_item_state(selected_item, 'none'))
            else:
                # Optionally, show disabled actions or a message
                action = menu.addAction("Cannot filter or exclude the root directory")
                action.setEnabled(False)
            menu.exec(self.viewport().mapToGlobal(position))

    def set_item_state(self, item, state):
        """Update item state and emit signal."""
        item.filter_state = state
        self.update_item_appearance(item)
        self.itemStateChanged.emit()

    def update_item_appearance(self, item):
        """Update the visual appearance of an item based on its state."""
        if item.filter_state == 'filter':
            item.setForeground(0, Qt.GlobalColor.darkGreen)
        elif item.filter_state == 'exclude':
            item.setForeground(0, Qt.GlobalColor.red)
        else:
            item.setForeground(0, Qt.GlobalColor.black)
        # Recursively update children
        for i in range(item.childCount()):
            child = item.child(i)
            if child.filter_state == 'none':
                self.update_item_appearance(child)

    def on_item_selection_changed(self):
        selected_items = self.selectedItems()
        if selected_items:
            self.itemSelected.emit(selected_items[0])
        else:
            self.itemSelected.emit(None)
