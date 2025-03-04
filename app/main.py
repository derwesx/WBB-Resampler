import sys
from PyQt5.QtWidgets import QApplication
from core.resampling import SWARII
from gui.app import FileProcessorApp
from config.settings import Config


def main():
    # Initialize application
    app = QApplication(sys.argv)

    # Create config instance
    config = Config()

    # Create resampling method
    resampling_method = SWARII(
        window_size=config.window_size,
        desired_frequency=config.desired_frequency
    )

    # Create and show the GUI
    window = FileProcessorApp(resampling_method)
    window.show()

    # Run the application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()