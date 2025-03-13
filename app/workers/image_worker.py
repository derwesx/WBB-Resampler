import os
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


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
        """Generate images for all CSV files in the output directory"""
        try:
            # Create images directory
            images_dir = os.path.join(self.output_dir, "_images")
            os.makedirs(images_dir, exist_ok=True)

            # Process each CSV file
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    if file.endswith(".csv") and "_csv" not in root and "_images" not in root:
                        file_path = os.path.join(root, file)
                        output_path = os.path.join(images_dir, os.path.basename(file_path).replace(".csv", ".jpg"))
                        self.log_callback(f"Generating image for {file_path}", color="blue")

                        try:
                            output_path = self.processor.generate_image(file_path, output_path)
                            self.log_callback(f"Image saved to {output_path}", color="green")
                        except Exception as e:
                            self.log_callback(f"Error generating image for {file_path}: {str(e)}", color="red")
        except Exception as e:
            self.log_callback(f"Error during image generation: {str(e)}", color="red")
        finally:
            self.finished_signal.emit()

    def log_callback(self, message, color="black"):
        """Emit log message signal to update the UI log"""
        self.log_signal.emit(message, color)
