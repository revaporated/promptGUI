from PyQt6.QtWidgets import QWidget, QLabel, QTextEdit, QVBoxLayout

class DetailsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.name_label = QLabel("")
        self.layout.addWidget(self.name_label)

        self.comment_edit = QTextEdit()
        self.comment_edit.setFontFamily("monospace")
        self.comment_edit.setPlaceholderText("Enter comment here...")
        self.comment_edit.textChanged.connect(self.on_comment_changed)
        self.layout.addWidget(self.comment_edit)

        self.current_item = None
        self.setEnabled(False)

    def update_details(self, item):
        self.current_item = item
        self.name_label.setText(f"{item.text(1)} Name: {item.text(0)}")
        self.comment_edit.setPlainText(item.comment)
        self.setEnabled(True)

    def clear_details(self):
        self.current_item = None
        self.name_label.setText("")
        self.comment_edit.clear()
        self.setEnabled(False)

    def on_comment_changed(self):
        if self.current_item:
            self.current_item.comment = self.comment_edit.toPlainText()
