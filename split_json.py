import json
import os

INPUT_FILE = 'anime_data.json'
ITEMS_PER_FILE = 30
OUTPUT_TEMPLATE = 'anime_data_part{}.json'

def split_dict(input_file, items_per_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, dict):
        print("الملف لا يحتوي على قاموس رئيسي!")
        return

    items = list(data.items())
    total = len(items)
    num_files = (total + items_per_file - 1) // items_per_file

    for i in range(num_files):
        start = i * items_per_file
        end = start + items_per_file
        chunk = dict(items[start:end])
        output_file = OUTPUT_TEMPLATE.format(i + 1)
        with open(output_file, 'w', encoding='utf-8') as out_f:
            json.dump(chunk, out_f, ensure_ascii=False, indent=2)
        print(f"تم إنشاء الملف: {output_file} ويحتوي على {len(chunk)} أنمي")

if __name__ == "__main__":
    split_dict(INPUT_FILE, ITEMS_PER_FILE) 