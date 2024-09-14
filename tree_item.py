from PyQt6.QtWidgets import QTreeWidgetItem

class TreeItem(QTreeWidgetItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.comment = ""
        self.filter_state = 'none'  # 'none', 'filter', 'exclude'
        self.path = ""  # Full path of the item
        self.is_filter_direct = False
        self.is_exclude_direct = False

    def set_filter(self, state, direct=True):
        """
        Set the filter state of the item.

        Args:
            state (str): 'none', 'filter', or 'exclude'
            direct (bool): True if set directly by the user, False if inherited
        """
        self.filter_state = state
        if state == 'filter':
            self.is_filter_direct = direct
            self.is_exclude_direct = False
        elif state == 'exclude':
            self.is_exclude_direct = direct
            self.is_filter_direct = False
        elif state == 'none':
            self.is_filter_direct = False
            self.is_exclude_direct = False

    def inherit_filter(self, state):
        """
        Inherit filter state from parent.

        Args:
            state (str): 'none', 'filter', or 'exclude'
        """
        if not (self.is_filter_direct or self.is_exclude_direct):
            self.filter_state = state
            # Since this is inherited, direct flags remain False

