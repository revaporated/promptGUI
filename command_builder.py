from PyQt6.QtWidgets import QLineEdit

class CommandBuilder(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("code2prompt command will appear here...")
        self.current_directory = ""

    def update_command(self, root_item):
        """
        Update the command based on the current tree state.
        
        Args:
            root_item (TreeItem): The root item of the directory tree.
        """
        filters = []
        excludes = []

        def collect_paths(item):
            """
            Recursively collect paths for filters and excludes.
            
            Args:
                item (TreeItem): The current tree item.
            """
            # If the item is directly excluded, add to excludes
            if item.filter_state == 'exclude' and item.is_exclude_direct:
                excludes.append(item.path)
            # If the item is directly filtered, add to filters
            elif item.filter_state == 'filter' and item.is_filter_direct:
                filters.append(item.path)
            # Traverse children to find direct excludes/filters
            for i in range(item.childCount()):
                child = item.child(i)
                collect_paths(child)

        collect_paths(root_item)

        command = f'code2prompt --path "{self.current_directory}"'
        if excludes:
            excludes_str = ','.join(f'"{p}"' for p in excludes)
            command += f' --exclude {excludes_str}'
        if filters:
            filters_str = ','.join(f'"{p}"' for p in filters)
            command += f' --filter {filters_str}'

        self.setText(command)
