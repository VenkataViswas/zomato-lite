import json
import csv
import os

json_files = ['file1.json', 'file2.json', 'file3.json', 'file4.json', 'file5.json']
csv_file = 'featured_images.csv'

csv_data = []

def extract_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        print(f"Processing file: {file_path}")
        for item in data:
            res_id = item.get('restaurant', {}).get('R', {}).get('res_id')
            featured_image = item.get('restaurant', {}).get('featured_image', '')
            print(f"ID: {res_id}, Image: {featured_image}")  # Debug print
            if res_id:
                csv_data.append({'id': res_id, 'featured_image': featured_image})

    for json_file in json_files:
        if os.path.exists(json_file):
            extract_data_from_json(json_file)
        else:
            print(f"File {json_file} does not exist.")

    if csv_data:
        with open(csv_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'featured_image'])
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"Data has been successfully written to {csv_file}.")
    else:
        print("No data extracted. Please check the JSON structure and extraction logic.")
