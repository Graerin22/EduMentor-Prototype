import os
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtGui import QTextCharFormat, QTextBlockFormat
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from core.document_parser import DocumentParser
from core.ai_engine import AIWorker
from core import file_manager

CURRENT_DIR = Path(__file__).resolve().parent
UI_FILE_PATH = CURRENT_DIR / 'chat_widget.ui'

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi(str(UI_FILE_PATH), self)

        self.messages = []
        self.document_text = ''
        self.filename = ''
        self.session_filepath = None

        last = file_manager.get_current_session()
        if last:
            self.load_session(last)

        self.upload_btn.clicked.connect(self.upload_file)
        self.newchat_btn.clicked.connect(self.new_chat)
        self.save_btn.clicked.connect(self.save_session)
        self.send_btn.clicked.connect(self.send_message)

    def load_session(self, filepath):
        self.save_session(silent=True)
    
        doc_name, doc_text, messages = file_manager.load_session(filepath)
        if not messages and not doc_text:
            QMessageBox.warning(self, 'Load Failed',
                                'The session file could not be read.')
            return

        self.session_filepath = filepath
        self.filename = doc_name
        self.document_text = doc_text
        self.messages = messages

        file_manager.set_current_session(filepath)
        self.on_document_loaded(self.document_text, self.filename)

        for msg in self.messages:
            cursor = self.ai_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)

            if msg['role'] == 'user':
                parts = msg['parts']
                if 'User Question:' in parts:
                    parts = parts.split('User Question:', 1)[1].strip()

                cursor.insertMarkdown("### 👤 You:&nbsp;\n")
                cursor.insertMarkdown(parts)
                cursor.insertText('\n\n')
            else:
                cursor.insertMarkdown("### 🧠 AI Tutor:&nbsp;\n")
                cursor.insertBlock()
                cursor.setBlockFormat(QTextBlockFormat())
                cursor.setCharFormat(QTextCharFormat())
                                
                cursor.insertMarkdown(msg['parts'])
                cursor.insertBlock()
                cursor.setBlockFormat(QTextBlockFormat())
                cursor.setCharFormat(QTextCharFormat())

            cursor.insertText('\n')
            self.ai_display.setTextCursor(cursor)

    def new_chat(self):
        has_content = bool(self.messages or self.document_text)
        if has_content:
            reply = QMessageBox.question(self, 'Start New Chat', 
                                         'Start a new chat? Your current session will be saved first.',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
            self.save_session(silent=True)
        
        self.messages = []
        self.document_text = ''
        self.filename = ''
        self.session_filepath = None

        self.upload_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.file_display.clear()
        self.ai_display.clear()
        self.input_text.clear()

    def save_session(self, silent=False):
        if not self.messages and not self.document_text:
            return
        if not getattr(self, 'session_filepath', None):
            self.session_filepath = file_manager.new_session_filepath()
        file_manager.save_session(self.session_filepath, self.filename, self.document_text, self.messages)
        file_manager.set_current_session(self.session_filepath)

        if not silent:
            self.ai_display.append('💾 Session saved!\n')
            self.save_btn.setEnabled(False)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select File',
                        filter='Documents (*.pdf *.docx *.pptx *.csv)')

        if file_path:
            self.send_btn.setEnabled(False)
            self.parser = DocumentParser(file_path)
            self.parser.finished.connect(self.on_document_loaded)
            self.parser.error.connect(self.on_parser_error)
            self.parser.start()

    def send_message(self):
        user_input = self.input_text.toPlainText().strip()
        if not user_input:
            return
        self.input_text.clear()
        self.send_btn.setEnabled(False)

        cursor = self.ai_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertMarkdown("### 👤 You:&nbsp;\n")
        cursor.insertMarkdown(f"{user_input}")
        cursor.insertText('\n\n')
        self.ai_display.setTextCursor(cursor)

        if not self.document_text:
            cursor = self.text_edit.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.deletePreviousChar()
            self.text_edit.setTextCursor(cursor)

            self.ai_display.append(f'⚠️ Please upload a document first.\n\n')
            self.send_btn.setEnabled(True)
            return

        self.system_prompt = """Role: AI Tutor
Explain the concepts from the provided document using clear, universal language and practical analogies.
CRITICAL FORMATTING RULES:
1. Write all math formulas using clean plain text unicode operators and true subscripts/superscripts (e.g., aₙ = 6aₙ₋₁).
2. Do NOT use LaTeX, MathJax, or raw dollar sign notation ($ or $$).
3. Do NOT generate Markdown matrix tables using pipes (|)."""

        if not self.messages:
            self.messages.append({'role':'user', 'parts':f'Source Doc:\n{self.document_text[:8000]}\n\nUser Question:\n{user_input}'})
        else:
            self.messages.append({'role':'user', 'parts':user_input})

        self.ai_worker = AIWorker(self.messages, self.system_prompt)
        self.ai_worker.finished.connect(self.on_ai_response)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_document_loaded(self, text, filename):
        self.file_display.clear()
        self.filename = filename
        self.document_text = text
        self.file_display.append(f'📄 Loaded: {filename}\n')

        cursor = self.file_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertMarkdown('---')
        cursor.insertMarkdown(text)
        self.file_display.setTextCursor(cursor)
        
        self.send_btn.setEnabled(True)
        self.upload_btn.setEnabled(False)

    def on_ai_response(self, response):
        cursor = self.ai_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertMarkdown("### 🧠 AI Tutor:&nbsp;\n")
        cursor.insertBlock()
        cursor.setBlockFormat(QTextBlockFormat())
        cursor.setCharFormat(QTextCharFormat())

        cursor.insertMarkdown(response)
        cursor.insertBlock()
        cursor.setBlockFormat(QTextBlockFormat())
        cursor.setCharFormat(QTextCharFormat())
        cursor.insertText('\n')
        self.ai_display.setTextCursor(cursor)

        self.messages.append({'role':'model', 'parts':response})
        
        self.send_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def on_parser_error(self, error_msg):
        self.file_display.append(f'❌ Error loading files: {error_msg}\n\n')
        self.send_btn.setEnabled(True)

    def on_ai_error(self, error_msg):
        self.ai_display.append(f'❌ Error: {error_msg}\n\n')
        self.messages.pop()
        self.send_btn.setEnabled(True)