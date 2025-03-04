import os
import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
from resampling import SWARII
import numpy as np
from datetime import datetime

# Load configuration from config.json
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

config = load_config()

def parse_wbb_file(file_address):
    time = []
    signal = []
    with open(file_address, 'rt') as f:
        f.readline()  # Skip first line
        f.readline()  # Skip second line

        for line in f:
            if line.strip():  # Only process non-empty lines
                data = line.split(" ")
                t = 0.001 * float(data[0])  # Convert to seconds
                x = float(data[5])
                y = float(data[6])
                time.append(t)
                signal.append([x, y])

    return np.array(time), np.array(signal)


def process_files(input_dir, resampling_method, output_dir, max_depth=1, log_callback=None):
    base_depth = input_dir.rstrip(os.sep).count(os.sep)
    errors = []  # List to store files that encounter errors

    for root, _, files in os.walk(input_dir):
        for file in files:
            current_depth = root.count(os.sep) - base_depth
            if current_depth > max_depth:
                break

            if file.isdigit():  # Check if the file name is a number (e.g., '1', '2', '3')
                file_path = os.path.join(root, file)
                if log_callback:
                    log_callback(f"Working on {file_path}")

                # Create output filename and check if it already exists
                relative_path = os.path.relpath(file_path, input_dir)
                output_subdir = os.path.join(output_dir, os.path.dirname(relative_path).replace(os.sep, '-'))
                output_filename = relative_path.replace(os.sep, '-')  # Replace path separators with hyphens
                output_path = os.path.join(output_subdir, output_filename)

                if os.path.exists(output_path):
                    if log_callback:
                        log_callback(f"Skipping {file_path}, already processed.")
                    continue

                try:
                    # Ensure the output subdirectory exists
                    os.makedirs(output_subdir, exist_ok=True)

                    # Parse the file and apply resampling
                    time, signal = parse_wbb_file(file_path)
                    resampled_time, resampled_signal = resampling_method.resample(time, signal)
                    resampled_combined = np.column_stack((resampled_time, resampled_signal))

                    # Save the resampled data
                    with open(output_path, 'w') as f:
                        f.write("Time(s) X(cm) Y(cm)\n")
                        np.savetxt(f, resampled_combined, fmt="%.9f", delimiter=" ")

                    if log_callback:
                        log_callback(f"Processed {file_path}")

                except Exception as e:
                    if log_callback:
                        log_callback(f"Error processing {file_path}: {e}")
                    errors.append(file_path)  # Add the file to the error list

    # Save error log if there were errors
    if errors:
        with open('errors.txt', 'w') as error_file:
            error_file.write("Files that encountered errors:\n")
            for error in errors:
                error_file.write(f"{error}\n")

    if log_callback:
        log_callback("Processing completed!")


class FileProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Resampler")

        # Use settings from config
        window_geometry = config.get("window_geometry", [100, 100, 800, 600])
        self.setGeometry(*window_geometry)  # Apply window size and position

        # Set up layout
        layout = QVBoxLayout()

        self.input_dir = ""
        self.output_dir = os.getcwd()  # Default output directory is the current working directory

        # Create a horizontal layout for input and output folder buttons
        folder_layout = QHBoxLayout()

        # Input folder button
        self.input_button = QPushButton("Select Input Folder")
        self.input_button.setStyleSheet(f"font-size: {config['input_button_font_size']}px; padding: {config['input_button_padding']}px;")
        self.input_button.clicked.connect(self.select_input_folder)
        folder_layout.addWidget(self.input_button)

        # Output folder button
        self.output_button = QPushButton("Select Output Folder")
        self.output_button.setStyleSheet(f"font-size: {config['output_button_font_size']}px; padding: {config['output_button_padding']}px;")
        self.output_button.clicked.connect(self.select_output_folder)
        folder_layout.addWidget(self.output_button)

        # Add folder layout to the main layout
        layout.addLayout(folder_layout)

        # Process button
        self.process_button = QPushButton("Process Files")
        self.process_button.setStyleSheet(f"font-size: {config['process_button_font_size']}px; padding: {config['process_button_padding']}px;")
        self.process_button.clicked.connect(self.process_files)
        layout.addWidget(self.process_button)

        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Text area to show logs
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(config['log_text_read_only'])  # Set read-only based on config
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def select_input_folder(self):
        self.input_dir = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        self.status_label.setText(f"Selected Input Folder: {self.input_dir}")
        self.update_log(f"Input Folder Selected: {self.input_dir}")  # Log input folder selection

    def select_output_folder(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        self.status_label.setText(f"Selected Output Folder: {self.output_dir}")
        self.update_log(f"Output Folder Selected: {self.output_dir}")  # Log output folder selection

    def process_files(self):
        if not self.input_dir:
            self.status_label.setText("Please select an input folder.")
            return

        resampling_method = SWARII(window_size=config["window_size"], desired_frequency=config["desired_frequency"])

        # Start processing and update logs
        self.log_text.clear()  # Clear previous logs
        self.update_log("Starting file processing...")
        process_files(self.input_dir, resampling_method, self.output_dir, max_depth=config["max_depth"], log_callback=self.update_log)
        self.status_label.setText("Processing completed!")

    def update_log(self, message):
        # Get the current time with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)  # Add new message with timestamp to the log area


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileProcessorApp()
    window.show()
    sys.exit(app.exec_())
