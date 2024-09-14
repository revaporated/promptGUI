from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QComboBox, QScrollArea, QMessageBox
)
from PyQt6.QtCore import QDir, Qt
from data_manager import DataManager
from tree_view import TreeView
from command_builder import CommandBuilder
from details_panel import DetailsPanel
from pathlib import Path
import re
from datetime import datetime
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("promptUI")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize DataManager
        self.trees_dir = Path(__file__).parent / 'trees'
        self.data_manager = DataManager(self.trees_dir)
        self.tree_titles = self.data_manager.tree_titles
        self.title_to_file = self.data_manager.title_to_file

        self.unsaved_changes = False
        self.current_tree_title = None
        self.current_directory = ""

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Load existing trees layout
        load_existing_layout = QHBoxLayout()
        self.load_combo = QComboBox()
        self.load_combo.addItem("-- Select Existing Tree --")
        self.load_combo.addItems(self.tree_titles)
        self.load_combo.currentIndexChanged.connect(self.load_selected_tree)
        load_existing_layout.addWidget(QLabel("Load Existing Tree:"))
        load_existing_layout.addWidget(self.load_combo)
        main_layout.addLayout(load_existing_layout)

        # Load new tree layout
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

        # Tree view setup
        self.tree_view = TreeView(self)
        self.tree_view.itemStateChanged.connect(self.on_tree_item_state_changed)
        self.tree_view.itemSelected.connect(self.on_item_selected)

        # Scroll area for the tree view
        tree_scroll_area = QScrollArea()
        tree_scroll_area.setWidgetResizable(True)
        tree_scroll_area.setWidget(self.tree_view)
        content_layout.addWidget(tree_scroll_area)

        # Details panel setup
        self.details_panel = DetailsPanel(self)
        details_scroll_area = QScrollArea()
        details_scroll_area.setWidgetResizable(True)
        details_scroll_area.setWidget(self.details_panel)
        content_layout.addWidget(details_scroll_area)

        # Command builder setup
        self.command_builder = CommandBuilder(self)
        main_layout.addWidget(QLabel("Command Builder:"))
        main_layout.addWidget(self.command_builder)

        # Status label and buttons at the bottom
        bottom_layout = QHBoxLayout()
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

    def refresh_load_combo(self):
        """Refresh the load_combo to reflect the current list of tree titles."""
        current_selection = self.load_combo.currentText()

        # Block signals to prevent triggering events during the update
        self.load_combo.blockSignals(True)

        # Clear existing items
        self.load_combo.clear()

        # Add the default prompt
        self.load_combo.addItem("-- Select Existing Tree --")

        # Add updated tree titles from DataManager
        self.load_combo.addItems(self.data_manager.tree_titles)

        # Restore the previous selection if it still exists
        if current_selection in self.data_manager.tree_titles:
            index = self.load_combo.findText(current_selection)
            self.load_combo.setCurrentIndex(index)
        else:
            self.load_combo.setCurrentIndex(0)  # Reset to default

        # Re-enable signals
        self.load_combo.blockSignals(False)

    def make_safe_filename(self, s):
        """Convert a string into a filename-safe string."""
        s = re.sub(r'[^\w\s-]', '', s)
        s = s.strip().replace(' ', '_')
        return s

    def browse_directory(self):
        """Open a dialog to select a directory and update the path input."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", QDir.homePath())
        if directory:
            self.path_input.setText(directory)
            self.load_tree_from_path(directory)  # Load the tree immediately

    def load_tree_from_path(self, directory=None):
        """Load and display the directory tree."""
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
        self.current_directory = str(path.resolve())
        self.directory_label.setText(f"Directory Path: {self.current_directory}")
        self.path_input.clear()

        try:
            self.tree_view.populate_tree(path)
            self.unsaved_changes = True  # New tree loaded, changes unsaved
            self.edit_title_button.setEnabled(True)
            self.update_status_label()
            # Update command builder
            self.command_builder.current_directory = self.current_directory
            root_item = self.tree_view.topLevelItem(0)
            self.command_builder.update_command(root_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the directory:\n{str(e)}")

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
                tree_data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tree '{title}':\n{str(e)}")
            return

        self.clear_tree_data()
        self.current_tree_title = title
        self.title_input.setText(title)
        self.title_input.setEnabled(False)
        self.title_input.setReadOnly(True)
        self.edit_title_button.setEnabled(True)
        self.cancel_edit_button.setVisible(False)

        self.current_directory = tree_data.get('path', '')
        self.directory_label.setText(f"Directory Path: {self.current_directory}")
        self.path_input.clear()

        try:
            self.tree_view.load_tree_from_json(tree_data['root'])
            self.unsaved_changes = False
            self.update_status_label()
            # Update command builder
            self.command_builder.current_directory = self.current_directory
            root_item = self.tree_view.topLevelItem(0)
            self.command_builder.update_command(root_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading the tree:\n{str(e)}")

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

        # Check if the title has changed
        title_changed = title != self.current_tree_title

        if title_changed and self.current_tree_title:
            # Renaming an existing tree
            success = self.data_manager.rename_tree(self.current_tree_title, title)
            if not success:
                return

            # Refresh the dropdown to reflect the renamed tree
            self.refresh_load_combo()

            # Update the current tree title
            self.current_tree_title = title
        else:
            # New tree or saving with the same title
            if title in self.data_manager.tree_titles:
                proceed = QMessageBox.question(
                    self,
                    "Duplicate Title",
                    f"A tree with the title '{title}' already exists. Do you want to overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if proceed != QMessageBox.StandardButton.Yes:
                    return

        # Build the tree JSON
        root_item = self.tree_view.topLevelItem(0)
        if not root_item:
            QMessageBox.warning(self, "No Tree Loaded", "There is no tree to save. Please load a directory tree first.")
            return

        root_json = self.tree_view.build_tree_json(root_item)

        # Save the tree using DataManager
        success = self.data_manager.save_tree(title, self.current_directory, root_json)
        if not success:
            return

        # Refresh the dropdown to include the newly saved tree
        self.refresh_load_combo()

        # Update the current tree title if it's a new tree
        if not title_changed:
            self.current_tree_title = title

        # Finalize UI updates
        self.title_input.setEnabled(False)
        self.title_input.setReadOnly(True)
        self.edit_title_button.setEnabled(True)
        self.cancel_edit_button.setVisible(False)
        self.unsaved_changes = False
        self.update_status_label()

        QMessageBox.information(self, "Tree Saved", f"Tree '{title}' has been saved successfully.")

    def on_tree_item_state_changed(self):
        """Update command builder when tree item state changes."""
        root_item = self.tree_view.topLevelItem(0)
        self.command_builder.update_command(root_item)
        self.unsaved_changes = True
        self.update_status_label()

    def on_item_selected(self, item):
        """Update details panel when an item is selected."""
        if item is not None:
            self.details_panel.update_details(item)
        else:
            self.details_panel.clear_details()

    def update_status_label(self):
        """Update the status label to reflect saved/unsaved changes."""
        if self.unsaved_changes:
            self.status_label.setText("Unsaved changes")
        else:
            self.status_label.setText("All changes saved")

    def clear_tree_data(self):
        """Clear all data related to the current tree."""
        self.tree_view.clear()
        self.current_tree_title = None
        self.current_directory = ""
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
        self.details_panel.clear_details()
        self.command_builder.clear()

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
