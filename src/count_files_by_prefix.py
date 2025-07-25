import os
import csv
import argparse


def count_files_by_prefix(data_dir, image_file_prefix='1.2.'):
    results = []
    for foldername, subfolders, filenames in os.walk(data_dir):
        if foldername.endswith('_bm'):
            # Only count files in the current folder, not subfolders
            files = [f for f in filenames if os.path.isfile(os.path.join(foldername, f))]
            if files:
                count_prefix = sum(f.startswith(image_file_prefix) for f in files)
                count_non_prefix = len(files) - count_prefix
            else:
                count_prefix, count_non_prefix = 0, 0
            results.append({
                'folder': foldername,
                'count_prefix': count_prefix,
                'count_non_prefix': count_non_prefix
            })
        
        return results # Only process the top-level folders


def export_to_csv(results, output_csv):
    with open(output_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['slide_id', 'image_files', 'ann_files'])
        for row in results:
            writer.writerow([row['folder'], row['count_prefix'], row['count_non_prefix']])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Count DICOM WSI objects and ANN objects.')
    parser.add_argument('data_dir', help='Root directory to scan')
    parser.add_argument('output_csv', help='CSV file to write results')
    args = parser.parse_args()

    results = count_files_by_prefix(args.data_dir)
    export_to_csv(results, args.output_csv)
