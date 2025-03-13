import os
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from adapted.descriptors import compute_all_features
from adapted.stabilogram.stato import Stabilogram


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
        self.x = float(x) if x and x.strip() else 0
        self.y = float(y) if y and y.strip() else 0

    @pyqtSlot()
    def process(self):
        """Process all files in the input directory"""
        try:
            self.processor.process_files(
                self.input_dir,
                self.output_dir,
                self.cut_option,
                self.x,
                self.y,
                max_depth=self.config.max_depth,
                log_callback=self.log_callback
            )
        except Exception as e:
            self.log_callback(f"Error during processing: {str(e)}", color="red")
        finally:
            self.finished_signal.emit()

    @pyqtSlot()
    def process_csv(self):
        """Generate summary CSV file from processed data files"""
        try:
            # Create the _csv directory if it doesn't exist
            csv_dir = os.path.join(self.output_dir, "_csv")
            os.makedirs(csv_dir, exist_ok=True)

            # Create the results CSV file with timestamp in name
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
            result_csv_path = os.path.join(csv_dir, f"{timestamp}.csv")

            # Create header row for the CSV
            header = self.config.get("csv_file_header")

            self.log_callback(f"Creating CSV file: {result_csv_path}", color="blue")

            # Open the result file for writing
            with open(result_csv_path, 'w') as result_file:
                result_file.write(f"{header}\n")

                # Process each CSV file
                for root, _, files in os.walk(self.output_dir):
                    for file in files:
                        if file.endswith(".csv") and "_csv" not in root and "_images" not in root:
                            file_path = os.path.join(root, file)
                            self.log_callback(f"Computing features for {file_path}", color="blue")

                            try:
                                df = pd.read_csv(str(file_path), sep=r'\s+', skiprows=1,
                                                 names=['Time', 'X', 'Y'])
                                stato = Stabilogram()
                                stato.from_array(array=np.array([df['X'], df['Y']]).T,
                                                 original_frequency=self.config.get("desired_frequency"), resample=False)
                                sway_density_radius = 0.3  # 3 mm
                                params_dic = {"sway_density_radius": sway_density_radius}
                                features = compute_all_features(stato, params_dic=params_dic)

                                # Write a row with the filename and features
                                result_row = f"{file}"
                                for feature_name in features:
                                    result_row += f",{features[feature_name]}"

                                result_file.write(f"{result_row}\n")
                                self.log_callback(f"Features added for {file}", color="green")

                            except Exception as e:
                                self.log_callback(f"Error processing file {file}: {str(e)}", color="red")

            self.log_callback(f"Feature extraction completed. Results saved to {result_csv_path}", color="green")
        except Exception as e:
            self.log_callback(f"Error during CSV generation: {str(e)}", color="red")
        finally:
            self.finished_signal.emit()

    def log_callback(self, message, color="black"):
        """Emit log message signal to update the UI log"""
        self.log_signal.emit(message, color)
