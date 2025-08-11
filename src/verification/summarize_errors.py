import os
import argparse
from pathlib import Path

def summarize_errors(source_dir):
    with open(os.path.join(source_dir, 'error_summary.txt'), 'w') as summary:
        # Walk through all files in the directory
        for filename in os.listdir(source_dir):
            if filename.endswith('_output.txt'):
                file_path = os.path.join(source_dir, filename)
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.startswith('Error'):
                            summary.write(f"{filename}: {line}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Summarize dicom3tools errors for better overview.') 
    parser.add_argument('source_dir', type=Path, help='Path to root dir containing dicom3tools output files.')
    args = parser.parse_args()

    summarize_errors(args.source_dir)
