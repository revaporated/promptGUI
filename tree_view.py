from PyQt6.QtWidgets import QTreeWidget, QMenu, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from tree_item import TreeItem

class TreeView(QTreeWidget):
    # Signals to communicate with other components
    itemStateChanged = pyqtSignal()
    itemSelected = pyqtSignal(object)
    
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
        self.update_item_appearance(root_item)

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
        root_item.path = path
        if filter_state in ['filter', 'exclude']:
            root_item.set_filter(filter_state, direct=True)
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
            child_item.path = path
            if filter_state in ['filter', 'exclude']:
                child_item.set_filter(filter_state, direct=True)
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
        # Check if setting filter/exclude on an item that is already inherited
        inherited_state = self.get_inherited_state(item)
        if state == 'filter':
            if inherited_state in ['filter', 'exclude']:
                QMessageBox.warning(
                    self,
                    "Action Not Allowed",
                    "Cannot directly filter this item as it is already being filtered or excluded through a parent directory."
                )
                return
        elif state == 'exclude':
            if inherited_state == 'exclude':
                QMessageBox.warning(
                    self,
                    "Action Not Allowed",
                    "Cannot directly exclude this item as it is already being excluded through a parent directory."
                )
                return

        # Update the item's filter_state and direct flags
        if state == 'filter':
            item.set_filter('filter', direct=True)
        elif state == 'exclude':
            item.set_filter('exclude', direct=True)
        else:
            item.set_filter('none', direct=False)
            # Inherit state from parent after removing exclusion
            inherited_state = self.get_inherited_state(item)
            if inherited_state in ['filter', 'exclude']:
                item.inherit_filter(inherited_state)

        # Update children's inherited states
        self.update_children_inheritance(item)

        # Update item appearance
        self.update_item_appearance(item)

        # Emit signal
        self.itemStateChanged.emit()

    def get_inherited_state(self, item):
        """Determine the inherited filter state from ancestors."""
        parent = item.parent()
        while parent:
            if parent.filter_state == 'exclude':
                return 'exclude'
            elif parent.filter_state == 'filter':
                return 'filter'
            parent = parent.parent()
        return 'none'

    def update_children_inheritance(self, parent_item):
        """Update the inherited filter/exclude states for all children."""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if parent_item.filter_state in ['filter', 'exclude']:
                inherited_state = parent_item.filter_state
                # If child does not have a direct state, inherit from parent
                if child.filter_state == 'none':
                    child.inherit_filter(inherited_state)
                    self.update_item_appearance(child)
                    # Recursively update descendants
                    self.update_children_inheritance(child)
            else:
                # Parent has no filter/exclude, so remove inherited states unless child has direct state
                if not (child.is_filter_direct or child.is_exclude_direct):
                    if child.filter_state in ['filter', 'exclude']:
                        child.inherit_filter('none')
                        self.update_item_appearance(child)
                        self.update_children_inheritance(child)

    def update_item_appearance(self, item):
        """Update the visual appearance of an item based on its state."""
        # Different colors for direct and inherited states
        if item.filter_state == 'filter':
            if item.is_filter_direct:
                item.setBackground(0, Qt.GlobalColor.darkGreen)
                item.setToolTip(0, "Filtered (direct)")
            else:
                item.setBackground(0, Qt.GlobalColor.green)
                item.setToolTip(0, "Filtered (inherited)")
        elif item.filter_state == 'exclude':
            if item.is_exclude_direct:
                item.setBackground(0, Qt.GlobalColor.red)
                item.setToolTip(0, "Excluded (direct)")
            else:
                item.setBackground(0, Qt.GlobalColor.darkRed)
                item.setToolTip(0, "Excluded (inherited)")
        else:
            # Reset background and set foreground to black
            item.setForeground(0, Qt.GlobalColor.black)
            item.setBackground(0, Qt.GlobalColor.transparent)
            item.setToolTip(0, "")

        # Recursively update children
        for i in range(item.childCount()):
            child = item.child(i)
            # If child has its own direct state, it already has its own appearance
            if child.filter_state != 'none' and (child.is_filter_direct or child.is_exclude_direct):
                self.update_item_appearance(child)
            else:
                # If no direct state, inherit from parent
                if parent := item:
                    if parent.filter_state in ['filter', 'exclude']:
                        child.filter_state = parent.filter_state
                        child.inherit_filter(parent.filter_state)
                    else:
                        child.filter_state = 'none'
                        child.inherit_filter('none')
                self.update_item_appearance(child)

    def on_item_selection_changed(self):
        selected_items = self.selectedItems()
        if selected_items:
            self.itemSelected.emit(selected_items[0])
        else:
            self.itemSelected.emit(None)
