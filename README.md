# RAID Configurations Demo

This Python script creates an interactive graphical demonstration of RAID (Redundant Array of Independent Disks) configurations, specifically RAID 0 (Striping), RAID 1 (Mirroring), and RAID 5 (Striping with Parity). It uses a GUI built with `tkinter` and `Pillow` to visualize how data is distributed across disks, with clickable blocks to explore detailed information about data segments, memory addresses, and parity calculations.

## Features
- Visualize RAID 0, RAID 1, RAID 5, and RAID 1+0 configurations with vibrant, rounded blocks.
- Click on blocks to see detailed information, including sample data, memory addresses, and parity calculations.
- Uses a 64-byte sample file (`sample.txt`) to simulate real data distribution.

## Prerequisites
Before running the script, ensure you have the following installed:

- **Python 3.12** (or later)
- **Pillow** (Python Imaging Library) version 11.1.0 or later
- **tkinter** (usually included with Python)

## Installation

1. **Download the Files**
   - Download `raid.py` and `sample.txt` to a directory of your choice on your computer.

2. **Install Dependencies**
   - Open a terminal or Command Prompt and navigate to the directory containing `raid.py`.
   - Install `Pillow` if not already installed:
     ```bash
     python -m pip install pillow
     ```
   - Verify `Pillow` and `tkinter` are installed:
     ```bash
     python -c "import PIL; print(PIL.__version__)"
     python -c "import tkinter; print(tkinter.TkVersion)"
     ```
     - Expected output: `11.1.0` for `PIL` and a version like `8.6` for `tkinter`.

3. **Ensure `sample.txt` Exists**
   - The script expects a file named `sample.txt` in the same directory with the content:
     ```
     This is a sample file to demonstrate RAID configurations with 64 bytes of data.
     ```
   - If missing, the script will create it automatically when run.

## Running the Script

1. Navigate to the directory containing `raid.py` (e.g., using `cd` in Command Prompt or PowerShell).
2. Run the script using Python:
   ```bash
   python raid.py