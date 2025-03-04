from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
from config.settings import Config
from core.processor import FileProcessor


class FileProcessorApp(QWidget):
    def __init__(self, resampling_method):
        super().__init__()
        self.config = Config()
        self.processor = FileProcessor(resampling_method)
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("File Resampler")
        self.setGeometry(*self.config.get("window_geometry"))

        # Create layout
        main_layout = QVBoxLayout()
        folder_layout = QHBoxLayout()

        # Create UI components
        self._create_folder_buttons(folder_layout)
        main_layout.addLayout(folder_layout)

        self._create_process_button(main_layout)
        self._create_status_and_log(main_layout)

        self.setLayout(main_layout)

    def _create_folder_buttons(self, layout):
        # Input folder button
        self.input_button = QPushButton("Select Input Folder")
        self.input_button.setStyleSheet(
            f"font-size: {self.config.get('input_button_font_size')}px; "
            f"padding: {self.config.get('input_button_padding')}px;"
        )
        self.input_button.clicked.connect(self.select_input_folder)
        layout.addWidget(self.input_button)

        # Output folder button
        self.output_button = QPushButton("Select Output Folder")
        self.output_button.setStyleSheet(
            f"font-size: {self.config.get('output_button_font_size')}px; "
            f"padding: {self.config.get('output_button_padding')}px;"
        )
        self.output_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.output_button)

    def _create_process_button(self, layout):
        self.process_button = QPushButton("Process Files")
        self.process_button.setStyleSheet(
            f"font-size: {self.config.get('process_button_font_size')}px; "
            f"padding: {self.config.get('process_button_padding')}px;"
        )
        self.process_button.clicked.connect(self.process_files)
        layout.addWidget(self.process_button)

    def _create_status_and_log(self, layout):
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Log text area
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(self.config.get('log_text_read_only', True))
        layout.addWidget(self.log_text)

    def select_input_folder(self):
        self.input_dir = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if self.input_dir:
            self.input_button.setText(f"Input: {self.input_dir}")
            self.status_label.setText(f"Selected Input Folder: {self.input_dir}")
            self.update_log(f"Input Folder Selected: {self.input_dir}")

    def select_output_folder(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if self.output_dir:
            self.output_button.setText(f"Output: {self.output_dir}")
            self.status_label.setText(f"Selected Output Folder: {self.output_dir}")
            self.update_log(f"Output Folder Selected: {self.output_dir}")

    def process_files(self):
        """Start file processing"""
        if not self.input_dir:
            self.status_label.setText("Please select an input folder.")
            return

        # Optional: Clear previous logs
        # self.log_text.clear()

        self.update_log("Starting file processing...")

        self.processor.process_files(
            self.input_dir,
            self.output_dir,
            max_depth=self.config.max_depth,
            log_callback=self.update_log
        )

        self.status_label.setText("Processing completed!")

    def update_log(self, message, color="black"):
        """Add a timestamped message to the log"""
        timestamp = datetime.now().strftime('%d:%H:%M:%S')
        log_message = f'[{timestamp}] <span style="color:{color}">{message}</span>'
        self.log_text.append(log_message)