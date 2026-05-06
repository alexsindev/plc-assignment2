import sys
import io
import contextlib
import traceback
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QHBoxLayout, QPlainTextEdit, QTextEdit, QSplitter, QFileDialog, QLabel,
)
from PySide6.QtCore import Qt
from example.components.lexica import MyLexer
from example.components.parsers import ASTParser
from example.components.memory import Memory

class CompilerIDE(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PLC Compiler IDE")
        self.resize(1200, 700)

        # =========================
        # CENTRAL WIDGET
        # =========================
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # =========================
        # TOOLBAR
        # =========================
        toolbar_layout = QHBoxLayout()

        self.run_button = QPushButton("Run")
        self.clear_button = QPushButton("Clear")
        self.open_button = QPushButton("Open")
        self.save_button = QPushButton("Save")

        toolbar_layout.addWidget(self.run_button)
        toolbar_layout.addWidget(self.clear_button)
        toolbar_layout.addWidget(self.open_button)
        toolbar_layout.addWidget(self.save_button)

        toolbar_layout.addStretch()

        main_layout.addLayout(toolbar_layout)

        # =========================
        # MAIN SPLITTER
        # =========================
        main_splitter = QSplitter(Qt.Horizontal)

        # =========================
        # CODE EDITOR
        # =========================
        self.code_editor = QPlainTextEdit()

        self.code_editor.setPlaceholderText(
            "Write your compiler code here..."
        )

        self.code_editor.setStyleSheet("""
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: Consolas;
            font-size: 14px;
            padding: 8px;
        """)

        main_splitter.addWidget(self.code_editor)

        # =========================
        # RIGHT SIDE SPLITTER
        # =========================
        right_splitter = QSplitter(Qt.Vertical)

        # =========================
        # OUTPUT PANEL
        # =========================
        output_container = QWidget()
        output_layout = QVBoxLayout()
        output_container.setLayout(output_layout)

        output_label = QLabel("Program Output")

        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)

        self.output_console.setStyleSheet("""
            background-color: #252526;
            color: #9cdcfe;
            font-family: Consolas;
            font-size: 13px;
            padding: 6px;
        """)

        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_console)

        # =========================
        # ERROR PANEL
        # =========================
        error_container = QWidget()
        error_layout = QVBoxLayout()
        error_container.setLayout(error_layout)

        error_label = QLabel("Error Messages")

        self.error_console = QTextEdit()
        self.error_console.setReadOnly(True)

        self.error_console.setStyleSheet("""
            background-color: #252526;
            color: #f14c4c;
            font-family: Consolas;
            font-size: 13px;
            padding: 6px;
        """)

        error_layout.addWidget(error_label)
        error_layout.addWidget(self.error_console)

        # Add widgets to right splitter
        right_splitter.addWidget(output_container)
        right_splitter.addWidget(error_container)

        # Add right splitter to main splitter
        main_splitter.addWidget(right_splitter)

        # Initial sizes
        main_splitter.setSizes([800, 400])
        right_splitter.setSizes([300, 300])

        # Add splitter to layout
        main_layout.addWidget(main_splitter)

        # =========================
        # BUTTON CONNECTIONS
        # =========================
        self.run_button.clicked.connect(self.run_code)
        self.clear_button.clicked.connect(self.clear_consoles)
        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(self.save_file)

    # =========================
    # RUN CODE
    # =========================
    def run_code(self):
        code = self.code_editor.toPlainText().strip()
        self.output_console.clear()
        self.error_console.clear()

        if not code:
            return

        parse_capture = io.StringIO()

        try:
            memory = Memory()
            memory.reset()

            with contextlib.redirect_stdout(parse_capture), \
                 contextlib.redirect_stderr(parse_capture):
                tree = ASTParser().parse(MyLexer().tokenize(code))

            if tree is None:
                errors = parse_capture.getvalue().strip()
                self.error_console.append(
                    errors or "Syntax error: could not parse program."
                )
                return

            tree.run(memory)

            for line in memory.output:
                self.output_console.append(line)

        except (TypeError, NameError, SyntaxError) as e:
            self.error_console.append(f"{type(e).__name__}: {e}")
        except Exception as e:
            self.error_console.append(traceback.format_exc())

    # =========================
    # CLEAR CONSOLES
    # =========================
    def clear_consoles(self):
        self.output_console.clear()
        self.error_console.clear()

    # =========================
    # OPEN FILE
    # =========================
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Text Files (*.txt *.plc *.src);;All Files (*)"
        )

        if file_name:
            with open(file_name, "r") as file:
                self.code_editor.setPlainText(file.read())

    # =========================
    # SAVE FILE
    # =========================
    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Text Files (*.txt *.plc *.src);;All Files (*)"
        )

        if file_name:
            with open(file_name, "w") as file:
                file.write(self.code_editor.toPlainText())


# =========================
# APPLICATION ENTRY
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CompilerIDE()
    window.show()

    sys.exit(app.exec())