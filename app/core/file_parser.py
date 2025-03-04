import numpy as np


def parse_wbb_file(file_address):
    """
    Parse Nintendo Wii Board data files

    Args:
        file_address: Path to the file

    Returns:
        Tuple of (time_array, signal_array)
    """
    time = []
    signal = []

    with open(file_address, 'rt') as f:
        # Skip header lines
        f.readline()
        f.readline()

        for line in f:
            if line.strip():  # Skip empty lines
                data = line.split(" ")
                t = 0.001 * float(data[0])  # Convert to seconds
                x = float(data[5])
                y = float(data[6])
                time.append(t)
                signal.append([x, y])

    return np.array(time), np.array(signal)