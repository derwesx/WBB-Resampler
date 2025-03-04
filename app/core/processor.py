import os
import numpy as np
from .file_parser import parse_wbb_file


class FileProcessor:
    def __init__(self, resampling_method):
        self.resampling_method = resampling_method
        self.errors = []

    def process_files(self, input_dir, output_dir, max_depth=1, log_callback=None):
        """Process files from input directory and save to output directory"""
        self.errors = []  # Reset errors list
        base_depth = input_dir.rstrip(os.sep).count(os.sep)

        log_callback("Starting processing:")
        for root, _, files in os.walk(input_dir):

            base_folder = os.path.basename(input_dir.rstrip(os.sep))
            relative_path = os.path.relpath(root, input_dir)
            log_path = f"{base_folder}/{relative_path}"
            if relative_path == ".":
                log_path = f"{base_folder}"

            if log_callback:
                log_callback(f"Walking | Current -> {log_path}")

            # Skip if we've gone too deep in the directory structure
            current_depth = root.count(os.sep) - base_depth
            if current_depth > max_depth:
                continue

            for file in files:
                self._process_file(root, file, input_dir, output_dir, log_callback)

        self._save_error_log()
        if log_callback:
            log_callback("Processing completed!")

    def _process_file(self, root, file, input_dir, output_dir, log_callback):
        file_path = os.path.join(root, file)

        # Create output path
        base_folder = os.path.basename(input_dir.rstrip(os.sep))
        relative_path = os.path.relpath(file_path, input_dir)
        log_path = f"{base_folder}/{relative_path}"
        if relative_path == ".":
            log_path = f"{base_folder}"
        output_subdir = os.path.join(output_dir, os.path.dirname(relative_path).replace(os.sep, '-'))
        output_filename = relative_path.replace(os.sep, '-')
        output_path = os.path.join(output_subdir, output_filename)

        # Skip if already processed
        if os.path.exists(output_path):
            if log_callback:
                log_callback(f"Skipping {log_path}, already processed.")
            return

        if log_callback:
            log_callback(f"Working on {log_path}")

        try:
            # Ensure output directory exists
            os.makedirs(output_subdir, exist_ok=True)

            # Process the file
            time, signal = parse_wbb_file(file_path)
            resampled_time, resampled_signal = self.resampling_method.resample(time, signal)
            resampled_combined = np.column_stack((resampled_time, resampled_signal))

            # Save the result
            with open(output_path, 'w') as f:
                f.write("Time(s) X(cm) Y(cm)\n")
                np.savetxt(f, resampled_combined, fmt="%.9f", delimiter=" ")

            if log_callback:
                log_callback(f"Processed {log_path}")
                log_callback(f"Saved to {output_path}")

        except Exception as e:
            if log_callback:
                log_callback(f"Error processing {log_path}: {e}")
            self.errors.append(file_path)

    def _save_error_log(self):
        """Save error log if there were errors"""
        if self.errors:
            with open('errors.txt', 'w') as error_file:
                error_file.write("Files that encountered errors:\n")
                for error in self.errors:
                    error_file.write(f"{error}\n")