import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class ImageProcessor:
    def __init__(self, config):
        self.config = config

    def generate_image(self, file_path, output_path):
        """
        Generate an image with 3 subplots from CSV data
        1. Anteroposterior(cm) x Mediolateral(cm) 2D view
        2. Mediolateral(cm) vs Time(s)
        3. Anteroposterior(cm) vs Time(s)
        """
        try:
            # Read data from CSV file
            df = pd.read_csv(file_path, sep=r'\s+', skiprows=1,
                             names=['Time', 'X', 'Y'])

            # Normalize time to start from 0 & Center the data
            df['Time'] = df['Time'] - df['Time'].min()
            df['X'] = df['X'] - df['X'].mean()
            df['Y'] = df['Y'] - df['Y'].mean()

            # Create figure with subplots
            fig = plt.figure(figsize=(self.config.get('figure_width', 10),
                                      self.config.get('figure_height', 8)))

            # 1. Anteroposterior(cm) x Mediolateral(cm) 2D view on the left
            ax1 = plt.subplot2grid((2, 5), (0, 0), rowspan=2, colspan=2)
            ax1.set_box_aspect(1)
            ax1.plot(df['X'], df['Y'],
                     self.config.get('plot_line_style', '-'),
                     color=self.config.get('trajectory_color', 'navy'),
                     linewidth=self.config.get('plot_line_width', 1.5))

            # Make the plot square with equal limits
            x_lim = max(df['X'].max(), abs(df['X'].min()))
            y_lim = max(df['Y'].max(), abs(df['Y'].min()))
            x_lim = max(x_lim, 1) + 0.5
            y_lim = max(y_lim, 1) + 0.5
            ax1.set_xlim(-x_lim, x_lim)
            ax1.set_ylim(-y_lim, y_lim)
            ax1.set_aspect('equal')  # Make the plot square

            ax1.set_xlabel('Mediolateral (cm)', fontsize=self.config.get('axis_font_size', 12))
            ax1.set_ylabel('Anteroposterior (cm)', fontsize=self.config.get('axis_font_size', 12))
            ax1.grid(False)

            # 2. Mediolateral(cm) vs Time(s) on the right top
            ax2 = plt.subplot2grid((2, 5), (0, 2), colspan=3)
            ax2.set_box_aspect(0.4)

            ax2.plot(df['Time'], df['X'],
                     self.config.get('plot_line_style', '-'),
                     color=self.config.get('mediolateral_color', 'navy'),
                     linewidth=self.config.get('plot_line_width', 1.5))

            # Set y-axis limits similar to the image (X)
            ax2.set_ylim(-x_lim, x_lim)

            ax2.set_title('Mediolateral (cm)', fontsize=self.config.get('title_font_size', 12))
            ax2.grid(False)

            # 3. Anteroposterior(cm) vs Time(s) on the right bottom
            ax3 = plt.subplot2grid((2, 5), (1, 2), colspan=3)
            ax3.set_box_aspect(0.4)

            ax3.plot(df['Time'], df['Y'],
                     self.config.get('plot_line_style', '-'),
                     color=self.config.get('anteroposterior_color', 'navy'),
                     linewidth=self.config.get('plot_line_width', 1.5))

            # Set y-axis limits similar to the image (Y)
            ax3.set_ylim(-y_lim, y_lim)

            ax3.set_xlabel('Time (s)', fontsize=self.config.get('axis_font_size', 12))
            ax3.set_title('Anteroposterior (cm)', fontsize=self.config.get('title_font_size', 12))
            ax3.grid(False)

            # Adjust layout
            plt.tight_layout()

            plt.savefig(output_path, dpi=self.config.get('dpi', 300))
            plt.close(fig)

            return output_path
        except Exception as e:
            return str(e)
