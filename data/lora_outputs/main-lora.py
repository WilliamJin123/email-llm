from csv_to_html import format_json_attributes, csv_to_html_comparison
from lora_output_parser import compare_lora_output_to_tests
import sys
import re
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python lora-main.py <lora_json> <test_csv>")
        sys.exit(1)
    
    lora_json = sys.argv[1]
    test_csv = sys.argv[2]
    output_csv = re.sub(r'.*-(\d+)\.json$', r'test_outputs-\1.csv', lora_json)
    
    compare_lora_output_to_tests(lora_json, test_csv, output_csv)
    
    # Convert the output CSV to HTML for better visualization
    html_output = output_csv.replace('.csv', '.html')
    csv_to_html_comparison(output_csv, html_output)