import json
import csv
import sys

def compare_lora_output_to_tests(lora_json, test_csv, output_csv):
    """
    Parse email JSON data and convert it to CSV format.
    """
    data = []
    with open(lora_json, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            data.append([])
            data[i] = json.loads(line.strip())
    with open(test_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        test_data = [{'test_output' if k == 'output' else k: v for k, v in row.items()} for row in reader]
    
    
    for i, item in enumerate(data):
        output = item['output']
        test_data[i]['lora_output'] = output
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = test_data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(test_data)

if __name__ == "__main__":
    compare_lora_output_to_tests('./lora_test_outputs.json', '../test_emails.csv', './test_outputs.csv')