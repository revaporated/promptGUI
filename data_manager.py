import json
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox
from utils import make_safe_filename


class DataManager:
    def __init__(self, trees_dir, parent=None):
        self.parent = parent  # Parent widget for message boxes
        self.trees_dir = Path(trees_dir)
        if not self.trees_dir.exists():
            self.trees_dir.mkdir()
        self.tree_titles = []
        self.title_to_file = {}
        self.load_trees_data()

    def load_trees_data(self):
        """Load trees data from individual JSON files in the 'trees' directory."""
        self.tree_titles = []
        self.title_to_file = {}
        for tree_file in self.trees_dir.glob('*.json'):
            try:
                with open(tree_file, 'r', encoding='utf-8') as f:
                    tree_data = json.load(f)
                    title = tree_data['title']
                    self.tree_titles.append(title)
                    self.title_to_file[title] = tree_file
            except json.JSONDecodeError:
                QMessageBox.critical(self.parent, "Error", f"Failed to decode {tree_file.name}. The file might be corrupted.")
                continue

    def save_tree(self, title, path, root_json):
        """
        Save the tree data to a JSON file.
        
        Returns True on success, False otherwise.
        """
        safe_title = make_safe_filename(title)
        tree_file = self.trees_dir / f"{safe_title}.json"

        tree_json = {
            "title": title,
            "path": path,
            "root": root_json
        }

        try:
            with open(tree_file, 'w', encoding='utf-8') as f:
                json.dump(tree_json, f, indent=2)
            # Update internal mappings
            if title not in self.tree_titles:
                self.tree_titles.append(title)
                self.title_to_file[title] = tree_file
            return True
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to save tree '{title}':\n{str(e)}")
            return False

    def rename_tree(self, old_title, new_title):
        """
        Rename an existing tree by creating a new JSON file and deleting the old one.
        
        Returns True on success, False otherwise.
        """
        if new_title in self.tree_titles:
            proceed = QMessageBox.question(
                self.parent,
                "Duplicate Title",
                f"A tree with the title '{new_title}' already exists. Do you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if proceed != QMessageBox.StandardButton.Yes:
                return False

        old_safe_title = make_safe_filename(old_title)
        new_safe_title = make_safe_filename(new_title)
        old_file = self.trees_dir / f"{old_safe_title}.json"
        new_file = self.trees_dir / f"{new_safe_title}.json"

        try:
            if new_file.exists():
                new_file.unlink()
            old_file.rename(new_file)
            # Update internal mappings
            self.title_to_file.pop(old_title, None)
            self.tree_titles.remove(old_title)
            self.title_to_file[new_title] = new_file
            self.tree_titles.append(new_title)
            return True
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to rename tree '{old_title}' to '{new_title}':\n{str(e)}")
            return False

    def delete_tree(self, title):
        """
        Delete a tree's JSON file.
        
        Returns True on success, False otherwise.
        """
        if title not in self.title_to_file:
            QMessageBox.warning(self.parent, "Warning", f"No tree found with the title '{title}'.")
            return False

        tree_file = self.title_to_file[title]
        try:
            tree_file.unlink()
            self.title_to_file.pop(title, None)
            self.tree_titles.remove(title)
            return True
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Failed to delete tree '{title}':\n{str(e)}")
            return False
