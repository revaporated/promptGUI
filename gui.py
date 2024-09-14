import sys
import json
import os
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QPushButton, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel,
    QScrollArea, QComboBox, QMenu, QInputDialog, QTextEdit
)
from PyQt6.QtCore import QDir, Qt
from pathlib import Path
from datetime import datetime


class Code2PromptGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code2Prompt GUI")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize trees data
        self.unsaved_changes = False  # Track unsaved changes
        self.current_tree_title = None  # Track the current tree title
        self.load_trees_data()

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Top layout for loading existing trees
        load_existing_layout = QHBoxLayout()
        self.load_combo = QComboBox()
        self.load_combo.addItem("-- Select Existing Tree --")
        self.load_combo.addItems(self.tree_titles)
        self.load_combo.currentIndexChanged.connect(self.load_selected_tree)
        load_existing_layout.addWidget(QLabel("Load Existing Tree:"))
        load_existing_layout.addWidget(self.load_combo)
        main_layout.addLayout(load_existing_layout)

        # Layout for loading new tree
        load_new_layout = QHBoxLayout()
        load_new_layout.addWidget(QLabel("Load New Tree:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter directory path here...")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_directory)
        load_new_layout.addWidget(self.path_input)
        load_new_layout.addWidget(browse_button)
        main_layout.addLayout(load_new_layout)

        # Label to display the loaded directory path
        self.directory_label = QLabel("")
        main_layout.addWidget(self.directory_label)

        # Layout for title editing
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Tree Title:"))
        self.title_input = QLineEdit()
        self.title_input.setReadOnly(True)
        self.title_input.setPlaceholderText("No title")
        self.title_input.setEnabled(False)  # Initially disabled
        title_layout.addWidget(self.title_input)

        self.edit_title_button = QPushButton("Edit Title")
        self.edit_title_button.setEnabled(False)  # Initially disabled
        self.edit_title_button.clicked.connect(self.enable_title_editing)
        title_layout.addWidget(self.edit_title_button)

        self.cancel_edit_button = QPushButton("Cancel")
        self.cancel_edit_button.setVisible(False)
        self.cancel_edit_button.clicked.connect(self.cancel_title_editing)
        title_layout.addWidget(self.cancel_edit_button)

        main_layout.addLayout(title_layout)

        # Horizontal layout for tree and details panel
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Tree widget setup
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name", "Type"])
        self.tree_widget.setColumnWidth(0, 400)
        self.tree_widget.setColumnWidth(1, 100)
        # Remove the comment column from the tree view
        # self.tree_widget.setColumnWidth(2, 300)
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # Remove context menu for editing comments
        # self.tree_widget.customContextMenuRequested.connect(self.open_context_menu)

        # Connect selection change signal to update details panel
        self.tree_widget.itemSelectionChanged.connect(self.update_details_panel)

        # Scroll area for the tree
        tree_scroll_area = QScrollArea()
        tree_scroll_area.setWidgetResizable(True)
        tree_scroll_area.setWidget(self.tree_widget)

        content_layout.addWidget(tree_scroll_area)

        # Details panel setup
        self.details_panel = QWidget()
        details_layout = QVBoxLayout()
        self.details_panel.setLayout(details_layout)

        # Label for file/directory name
        self.name_label = QLabel("")
        details_layout.addWidget(self.name_label)

        # Comment editor
        self.comment_edit = QTextEdit()
        self.comment_edit.setFontFamily("monospace")
        self.comment_edit.setPlaceholderText("Enter comment here...")
        self.comment_edit.textChanged.connect(self.comment_text_changed)
        details_layout.addWidget(self.comment_edit)

        # Initially disable the details panel
        self.details_panel.setEnabled(False)

        # Scroll area for details panel
        details_scroll_area = QScrollArea()
        details_scroll_area.setWidgetResizable(True)
        details_scroll_area.setWidget(self.details_panel)

        content_layout.addWidget(details_scroll_area)

        # Status label and buttons at the bottom
        bottom_layout = QHBoxLayout()

        # Status label to show saved/unsaved changes
        self.status_label = QLabel("No changes")
        bottom_layout.addWidget(self.status_label)

        bottom_layout.addStretch()

        # Close Tree button
        self.close_button = QPushButton("Close Tree")
        self.close_button.clicked.connect(self.close_tree)
        bottom_layout.addWidget(self.close_button)

        # Save button
        self.save_button = QPushButton("Save Tree")
        self.save_button.clicked.connect(self.save_tree)
        bottom_layout.addWidget(self.save_button)

        main_layout.addLayout(bottom_layout)

    def make_safe_filename(self, s):
        """Convert a string into a filename-safe string."""
        s = re.sub(r'[^\w\s-]', '', s)
        s = s.strip().replace(' ', '_')
        return s

    def load_trees_data(self):
        """Load trees data from individual JSON files in the 'trees' directory."""
        self.tree_titles = []
        self.title_to_file = {}
        self.trees_dir = Path(__file__).parent / 'trees'
        if not self.trees_dir.exists():
            self.trees_dir.mkdir()
        for tree_file in self.trees_dir.glob('*.json'):
            try:
                with open(tree_file, 'r', encoding='utf-8') as f:
                    tree_data = json.load(f)
                    title = tree_data['title']
                    self.tree_titles.append(title)
                    self.title_to_file[title] = tree_file
            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", f"Failed to decode {tree_file.name}. The file might be corrupted.")
                continue

    def browse_directory(self):
        """Open a dialog to select a directory and update the path input."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", QDir.homePath())
        if directory:
            self.path_input.setText(directory)
            self.load_tree_from_path(directory)  # Load the tree immediately

    def load_tree_from_path(self, directory=None):
        """Load and display the directory tree in the tree widget."""
        if directory is None:
            path_str = self.path_input.text().strip()
        else:
            path_str = directory

        if not path_str:
            QMessageBox.warning(self, "Input Required", "Please enter or select a directory path.")
            return

        if self.unsaved_changes:
            proceed = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to discard them and load a new tree?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if proceed != QMessageBox.StandardButton.Yes:
                return

        path = Path(path_str)
        if not path.exists() or not path.is_dir():
            QMessageBox.warning(self, "Invalid Directory", "The selected directory does not exist or is not a directory.")
            return

        self.clear_tree_data()
        self.directory_label.setText(f"Directory Path: {path_str}")
        self.path_input.clear()

        try:
            root_item = QTreeWidgetItem([path.name, "Directory"])
            root_item.comment = ""
            self.tree_widget.addTopLevelItem(root_item)
            self.populate_tree(root_item, path)
            root_item.setExpanded(True)
            self.unsaved_changes = True  # New tree loaded, changes unsaved
            self.edit_title_button.setEnabled(True)
            self.update_status_label()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the directory:\n{str(e)}")

    def populate_tree(self, parent_item, path):
        """Recursively populate the tree widget with directory contents."""
        try:
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if item.is_dir():
                    child_item = QTreeWidgetItem([item.name, "Directory"])
                    child_item.comment = ""
                    parent_item.addChild(child_item)
                    self.populate_tree(child_item, item)
                else:
                    child_item = QTreeWidgetItem([item.name, "File"])
                    child_item.comment = ""
                    parent_item.addChild(child_item)
        except PermissionError:
            child_item = QTreeWidgetItem(["[Permission Denied]", "Directory"])
            child_item.comment = ""
            parent_item.addChild(child_item)
        except Exception as e:
            child_item = QTreeWidgetItem([f"[Error: {str(e)}]", "File"])
            child_item.comment = ""
            parent_item.addChild(child_item)

    def enable_title_editing(self):
        """Enable the title input field for editing."""
        self.title_input.setEnabled(True)
        self.title_input.setReadOnly(False)
        self.title_input.setFocus()
        self.edit_title_button.setEnabled(False)
        self.cancel_edit_button.setVisible(True)
        self.unsaved_changes = True
        self.update_status_label()

    def cancel_title_editing(self):
        """Cancel the title editing."""
        if self.current_tree_title:
            self.title_input.setText(self.current_tree_title)
        else:
            self.title_input.clear()
        self.title_input.setEnabled(False)
        self.title_input.setReadOnly(True)
        self.edit_title_button.setEnabled(True)
        self.cancel_edit_button.setVisible(False)
        self.unsaved_changes = False
        self.update_status_label()

    def save_tree(self):
        """Save the current tree to its own JSON file."""
        title = self.title_input.text().strip()

        if not title:
            proceed = QMessageBox.question(
                self,
                "No Title Provided",
                "You did not provide a title for the tree. Do you want to proceed with an auto-generated title?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if proceed == QMessageBox.StandardButton.Yes:
                timestamp = datetime.now().strftime('%m-%d-%y-%H-%M-%S')
                title = f"Untitled_{timestamp}"
                self.title_input.setText(title)
            else:
                return

        # Generate a safe filename from the title
        safe_title = self.make_safe_filename(title)
        tree_file = self.trees_dir / f"{safe_title}.json"

        # Check if the title has changed
        title_changed = title != self.current_tree_title

        if title_changed and self.current_tree_title:
            # Renaming an existing tree
            old_safe_title = self.make_safe_filename(self.current_tree_title)
            old_tree_file = self.trees_dir / f"{old_safe_title}.json"

            if tree_file.exists():
                proceed = QMessageBox.question(
                    self,
                    "Duplicate Title",
                    f"A tree with the title '{title}' already exists. Do you want to overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if proceed != QMessageBox.StandardButton.Yes:
                    return

            # Save the tree to the new file
            success = self.save_tree_to_file(tree_file, title)
            if not success:
                return

            # Delete the old file
            try:
                if old_tree_file.exists():
                    old_tree_file.unlink()
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to delete old tree file:\n{str(e)}")

            # Update the titles list and mappings
            self.tree_titles.remove(self.current_tree_title)
            self.tree_titles.append(title)
            self.title_to_file.pop(self.current_tree_title, None)
            self.title_to_file[title] = tree_file

            # Update the load_combo
            index = self.load_combo.findText(self.current_tree_title)
            if index >= 0:
                self.load_combo.setItemText(index, title)
            else:
                self.load_combo.addItem(title)

            self.current_tree_title = title
        else:
            # New tree or saving with the same title
            if tree_file.exists():
                proceed = QMessageBox.question(
                    self,
                    "Duplicate Title",
                    f"A tree with the title '{title}' already exists. Do you want to overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if proceed != QMessageBox.StandardButton.Yes:
                    return

            # Save the tree to the file
            success = self.save_tree_to_file(tree_file, title)
            if not success:
                return

            if title not in self.tree_titles:
                self.tree_titles.append(title)
                self.title_to_file[title] = tree_file
                self.load_combo.addItem(title)

            self.current_tree_title = title

        self.title_input.setEnabled(False)
        self.title_input.setReadOnly(True)
        self.edit_title_button.setEnabled(True)
        self.cancel_edit_button.setVisible(False)
        self.unsaved_changes = False
        self.update_status_label()

        QMessageBox.information(self, "Tree Saved", f"Tree '{title}' has been saved successfully.")

    def save_tree_to_file(self, tree_file, title):
        """Helper method to save the tree data to a file."""
        # Get the root item
        root = self.tree_widget.topLevelItem(0)
        if not root:
            QMessageBox.warning(self, "No Tree Loaded", "There is no tree to save. Please load a directory tree first.")
            return False

        path = self.directory_label.text().replace("Directory Path: ", "").strip()

        tree_json = {
            "title": title,
            "path": path,
            "root": self.build_tree_json(root)
        }

        # Save the tree to its json file
        try:
            with open(tree_file, 'w', encoding='utf-8') as f:
                json.dump(tree_json, f, indent=2)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save tree '{title}':\n{str(e)}")
            return False

    def build_tree_json(self, item):
        """Recursively build the JSON representation of the tree."""
        node = {
            "name": item.text(0),
            "type": item.text(1).lower(),
            "comment": getattr(item, 'comment', ''),
        }
        if item.childCount() > 0:
            node["contents"] = []
            for i in range(item.childCount()):
                child = item.child(i)
                node["contents"].append(self.build_tree_json(child))
        return node

    def load_selected_tree(self, index):
        """Load a tree from its JSON file based on the selected title."""
        if index == 0:
            # "-- Select Existing Tree --" selected
            return

        if self.unsaved_changes:
            proceed = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to discard them and load a new tree?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if proceed != QMessageBox.StandardButton.Yes:
                return

        title = self.load_combo.currentText()

        tree_file = self.title_to_file.get(title)
        if tree_file is None or not tree_file.exists():
            QMessageBox.warning(self, "Tree Not Found", f"The tree file for '{title}' was not found.")
            return

        try:
            with open(tree_file, 'r', encoding='utf-8') as f:
                tree = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tree '{title}':\n{str(e)}")
            return

        self.clear_tree_data()

        # Update the GUI
        self.current_tree_title = title
        self.title_input.setText(title)
        self.title_input.setEnabled(False)
        self.title_input.setReadOnly(True)
        self.edit_title_button.setEnabled(True)
        self.cancel_edit_button.setVisible(False)
        self.directory_label.setText(f"Directory Path: {tree.get('path', '')}")
        self.path_input.clear()

        self.tree_widget.clear()
        try:
            root_json = tree['root']
            root_item = QTreeWidgetItem([root_json['name'], root_json['type'].capitalize()])
            root_item.comment = root_json.get('comment', '')
            self.tree_widget.addTopLevelItem(root_item)
            self.populate_tree_from_json(root_item, root_json)
            root_item.setExpanded(True)
            self.unsaved_changes = False
            self.update_status_label()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the tree:\n{str(e)}")

    def populate_tree_from_json(self, parent_item, node_json):
        """Recursively populate the tree widget from JSON data."""
        contents = node_json.get('contents', [])
        for child in contents:
            name = child.get('name', '')
            type_ = child.get('type', '').capitalize()
            comment = child.get('comment', '')
            child_item = QTreeWidgetItem([name, type_])
            child_item.comment = comment
            parent_item.addChild(child_item)
            if type_.lower() == "directory":
                self.populate_tree_from_json(child_item, child)

    def update_status_label(self):
        """Update the status label to reflect saved/unsaved changes."""
        if self.unsaved_changes:
            self.status_label.setText("Unsaved changes")
        else:
            self.status_label.setText("All changes saved")

    def clear_tree_data(self):
        """Clear all data related to the current tree."""
        self.tree_widget.clear()
        self.current_tree_title = None
        self.unsaved_changes = False
        self.title_input.setText("")
        self.title_input.setEnabled(False)
        self.title_input.setReadOnly(True)
        self.edit_title_button.setEnabled(False)
        self.cancel_edit_button.setVisible(False)
        self.directory_label.setText("")
        self.path_input.clear()
        self.load_combo.setCurrentIndex(0)
        self.update_status_label()
        self.details_panel.setEnabled(False)
        self.name_label.setText("")
        self.comment_edit.clear()

    def close_tree(self):
        """Close the current tree."""
        if self.unsaved_changes:
            proceed = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to discard them and close the tree?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if proceed != QMessageBox.StandardButton.Yes:
                return

        self.clear_tree_data()

    def closeEvent(self, event):
        """Handle actions on closing the application."""
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self,
                'Unsaved Changes',
                'You have unsaved changes. Do you really want to quit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

        event.accept()

    def update_details_panel(self):
        """Update the details panel when a tree item is selected."""
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            item_type = item.text(1)
            name = item.text(0)
            comment = getattr(item, 'comment', '')

            self.name_label.setText(f"{item_type} Name: {name}")
            self.comment_edit.setPlainText(comment)
            self.details_panel.setEnabled(True)
        else:
            # No item selected
            self.details_panel.setEnabled(False)
            self.name_label.setText("")
            self.comment_edit.clear()

    def comment_text_changed(self):
        """Update the comment of the selected item when the text changes."""
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            item.comment = self.comment_edit.toPlainText()
            self.unsaved_changes = True
            self.update_status_label()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Code2PromptGUI()
    window.show()
    sys.exit(app.exec())
