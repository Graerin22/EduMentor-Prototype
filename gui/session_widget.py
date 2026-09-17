import os
from PyQt6 import uic
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QListWidgetItem, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from core import file_manager

CURRENT_DIR = Path(__file__).resolve().parent
UI_FILE_PATH = CURRENT_DIR / 'session_widget.ui'

class SessionWidget(QWidget):
    session_load_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        uic.loadUi(str(UI_FILE_PATH), self)

        self.selected_path = None

        self.list_widget.itemClicked.connect(self.on_item_selected)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.refresh_btn.clicked.connect(self.refresh_list)
        self.load_btn.clicked.connect(self.request_load_selected)
        self.rename_btn.clicked.connect(self.rename_selected)
        self.delete_btn.clicked.connect(self.delete_selected)

    def refresh_list(self):
        self.list_widget.clear()
        self.selected_path = None

        sessions = file_manager.list_sessions()
        current = file_manager.get_current_session()

        if not sessions:
            item = QListWidgetItem('(no sessions yet)')
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            self.update_btn_state()
            return

        for filepath, ts, size in sessions:
            doc_name = file_manager.get_session_document_name(filepath)
            msg_count = file_manager.count_messages(filepath)
            size_kb = size // 1024

            is_current = (filepath == current)
            marker = '⭐ ' if is_current else ''
            label = f'{marker}{ts} - {doc_name}\n   {msg_count} messages · {size_kb} KB · {os.path.basename(filepath)}'

            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            self.list_widget.addItem(item)

    def update_btn_state(self):
        has_selection = self.selected_path is not None
        self.load_btn.setEnabled(has_selection)
        self.rename_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def on_item_selected(self, item):
        filepath = item.data(Qt.ItemDataRole.UserRole)

        if not filepath:
            self.selected_path = None
            self.update_btn_state()
            return

        self.selected_path = filepath
        self.update_btn_state()

    def on_item_double_clicked(self, item):
        filepath = item.data(Qt.ItemDataRole.UserRole)

        if filepath:
            self.selected_path = filepath
            self.request_load_selected()

    def request_load_selected(self):
        if not self.selected_path:
            return
        self.session_load_requested.emit(self.selected_path)

    def rename_selected(self):
        if not self.selected_path:
            return

        curr_name = os.path.splitext(os.path.basename(self.selected_path))[0]
        new_name, ok = QInputDialog.getText(self, 'Rename Session', 
                                            'Enter a new name: ', text=curr_name)
        if not ok or not new_name.strip():
            return

        new_path = file_manager.rename_session(self.selected_path, new_name)
        if new_path:
            QMessageBox.information(self, 'Renamed', f'Session renamed to:\n{os.path.basename(new_path)}')
            self.refresh_list()
        else:
            QMessageBox.warning(self, 'Rename Failed', 'Could not rename the session. The name may be invalid or already in use.')

    def delete_selected(self):
        if not self.selected_path:
            return

        name = os.path.basename(self.selected_path)
        reply = QMessageBox.question(self, 'Delete Session',
                                     f'Are you sure you want to delete:\n\n{name}\n\n', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        if file_manager.delete_session(self.selected_path):
            self.refresh_list()
        else:
            QMessageBox.warning(self, 'Delete Failed',
                                'The session file could not be deleted.')