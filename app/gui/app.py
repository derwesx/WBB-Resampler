import os
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, \
    QRadioButton, QLineEdit
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from config.settings import Config
from core.file_processor import FileProcessor
from core.image_processor import ImageProcessor


class ProcessorApp(QWidget):
    def __init__(self, resampling_method):
        super().__init__()
        self.config = Config()
        self.file_processor = FileProcessor(resampling_method)
        self.image_processor = ImageProcessor(self.config)
        self.input_dir = ""
        self.output_dir = ""
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("File Resampler")
        self.setGeometry(*self.config.get("window_geometry"))

        # Create layout
        main_layout = QVBoxLayout()
        cut_layout = QHBoxLayout()
        folder_layout = QHBoxLayout()

        # Create UI components
        self._create_folder_buttons(folder_layout)
        main_layout.addLayout(folder_layout)

        self._create_cutting_options(cut_layout)
        main_layout.addLayout(cut_layout)

        self._create_process_button(main_layout)
        self._create_status_and_log(main_layout)

        self.setLayout(main_layout)

    def _create_cutting_options(self, layout):
        # Create radio buttons for cutting options
        self.none_cut_radio = QRadioButton("None cutting")
        self.first_way_cut_radio = QRadioButton("Cut first X seconds and last Y seconds")
        self.second_way_cut_radio = QRadioButton("Cut first X seconds and take Y seconds after")

        self.none_cut_radio.setChecked(True)  # Default to None cutting

        self.none_cut_radio.toggled.connect(lambda: self.set_cut_option(0))
        self.first_way_cut_radio.toggled.connect(lambda: self.set_cut_option(1))
        self.second_way_cut_radio.toggled.connect(lambda: self.set_cut_option(2))

        # Create input fields for X and Y
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("X seconds")
        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Y seconds")

        # Add to layout
        cut_layout = QHBoxLayout()
        cut_layout.addWidget(self.none_cut_radio)
        cut_layout.addWidget(self.first_way_cut_radio)
        cut_layout.addWidget(self.second_way_cut_radio)
        layout.addLayout(cut_layout)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.x_input)
        input_layout.addWidget(self.y_input)
        layout.addLayout(input_layout)

    def set_cut_option(self, option):
        self.cut_option = option

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

        self.image_button = QPushButton("Generate Images")
        self.image_button.setStyleSheet(
            f"font-size: {self.config.get('process_button_font_size')}px; "
            f"padding: {self.config.get('process_button_padding')}px;"
        )
        self.image_button.clicked.connect(self.generate_images)
        layout.addWidget(self.image_button)

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
            self.input_button.setText(
                f"Input: ...{self.input_dir[-self.config.max_text_length:] if len(self.input_dir) > self.config.max_text_length else self.input_dir}")
            self.status_label.setText(f"Selected Input Folder: {self.input_dir}")
            self.update_log(f"Input Folder Selected: {self.input_dir}")

    def select_output_folder(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if self.output_dir:
            self.output_button.setText(
                f"Output: ...{self.output_dir[-self.config.max_text_length:] if len(self.output_dir) > self.config.max_text_length else self.output_dir}")
            self.status_label.setText(f"Selected Output Folder: {self.output_dir}")
            self.update_log(f"Output Folder Selected: {self.output_dir}")

    def process_files(self):
        """Start file processing"""
        if not self.input_dir:
            self.status_label.setText("Please select an input folder.")
            return

        if not self.output_dir:
            self.update_log("Output folder not selected.", color="red")
            self.output_dir = os.path.expanduser(self.config.default_output_dir)
            self.output_button.setText(
                f"Output: ...{self.output_dir[-self.config.max_text_length:] if len(self.output_dir) > self.config.max_text_length else self.output_dir}")
            self.update_log(f"Default: {self.output_dir}", color="red")
            self.update_log(f"New output folder: {os.path.abspath(self.output_dir)}", color="red")
        # Optional: Clear previous logs
        # self.log_text.clear()

        self.update_log("Starting file processing...")

        # Create a QThread object
        self.file_thread = QThread()
        # Create a worker object
        self.file_worker = FileProcessorWorker(self.file_processor, self.input_dir, self.output_dir, self.config,
                                               self.cut_option,
                                               self.x_input.text(), self.y_input.text())
        # Move the worker to the thread
        self.file_worker.moveToThread(self.file_thread)
        # Connect signals and slots
        self.file_thread.started.connect(self.file_worker.process)
        self.file_worker.log_signal.connect(self.update_log)
        self.file_worker.finished_signal.connect(self.file_thread.quit)
        self.file_worker.finished_signal.connect(self.file_worker.deleteLater)
        self.file_thread.finished.connect(self.file_thread.deleteLater)
        # Start the thread
        self.file_thread.start()

        self.file_thread.finished.connect(lambda: self.status_label.setText("Processing completed!"))

    def generate_images(self):
        """Generate images from processed files in the output folder"""
        if not self.output_dir:
            self.status_label.setText("Please select an output folder.")
            return

        self.update_log("Starting image generation...")

        # Create a QThread object
        self.image_thread = QThread()
        # Create a worker object
        self.image_worker = ImageProcessorWorker(self.image_processor, self.output_dir, self.config)
        # Move the worker to the thread
        self.image_worker.moveToThread(self.image_thread)
        # Connect signals and slots
        self.image_thread.started.connect(self.image_worker.process)
        self.image_worker.log_signal.connect(self.update_log)
        self.image_worker.finished_signal.connect(self.image_thread.quit)
        self.image_worker.finished_signal.connect(self.image_worker.deleteLater)
        self.image_thread.finished.connect(self.image_thread.deleteLater)
        # Start the thread
        self.image_thread.start()

        self.image_thread.finished.connect(lambda: self.status_label.setText("Image generation completed!"))

    def update_log(self, message, color="black"):
        """Add a timestamped message to the log"""
        timestamp = datetime.now().strftime('%d:%H:%M:%S')
        log_message = f'[{timestamp}] <span style="color:{color}">{message}</span>'
        self.log_text.append(log_message)


class FileProcessorWorker(QObject):
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, processor, input_dir, output_dir, config, cut_option, x, y):
        super().__init__()
        self.processor = processor
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.config = config
        self.cut_option = cut_option
        self.x = float(x) if x else 0
        self.y = float(y) if y else 0

    @pyqtSlot()
    def process(self):
        self.processor.process_files(
            self.input_dir,
            self.output_dir,
            self.cut_option,
            self.x,
            self.y,
            max_depth=self.config.max_depth,
            log_callback=self.log_callback
        )
        self.finished_signal.emit()

    def log_callback(self, message, color="black"):
        self.log_signal.emit(message, color)


class ImageProcessorWorker(QObject):
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, processor, output_dir, config):
        super().__init__()
        self.processor = processor
        self.output_dir = output_dir
        self.config = config

    @pyqtSlot()
    def process(self):
        for root, _, files in os.walk(self.output_dir):

            base_folder = os.path.basename(self.output_dir.rstrip(os.sep))
            relative_path = os.path.relpath(root, self.output_dir)
            log_path = f"{base_folder}/{relative_path}"
            if relative_path == ".":
                log_path = f"{base_folder}"

            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    images_dir = os.path.join(self.output_dir, "images")
                    os.makedirs(images_dir, exist_ok=True)
                    output_path = os.path.join(images_dir, os.path.basename(file_path).replace(".csv", ".jpg"))
                    self.log_callback(f"Generating image for {file_path}", color="blue")

                    try:
                        output_path = self.processor.generate_image(file_path, output_path)
                        self.log_callback(f"Image saved to {output_path}", color="green")
                    except Exception as e:
                        self.log_callback(f"Error generating image: {str(e)}", color="red")

        self.finished_signal.emit()

    def log_callback(self, message, color="black"):
        self.log_signal.emit(message, color)
