from PyQt6.QtWidgets import QLineEdit

class CommandBuilder(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("code2prompt command will appear here...")
        self.current_directory = ""

    def update_command(self, root_item):
        filters = []
        excludes = []

        def collect_paths(item, inherited_state=None):
            current_state = item.filter_state if item.filter_state != 'none' else inherited_state
            if current_state == 'exclude':
                excludes.append(item.path)
                for i in range(item.childCount()):
                    child = item.child(i)
                    collect_paths(child, 'exclude')
            elif current_state == 'filter':
                filters.append(item.path)
                for i in range(item.childCount()):
                    child = item.child(i)
                    collect_paths(child, 'filter')
            else:
                for i in range(item.childCount()):
                    child = item.child(i)
                    collect_paths(child, inherited_state)

        collect_paths(root_item)

        command = f'code2prompt --path "{self.current_directory}"'
        if excludes:
            excludes_str = ','.join(f'"{p}"' for p in excludes)
            command += f' --exclude {excludes_str}'
        if filters:
            filters_str = ','.join(f'"{p}"' for p in filters)
            command += f' --filter {filters_str}'

        self.setText(command)

